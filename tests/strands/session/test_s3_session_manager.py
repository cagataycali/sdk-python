"""Tests for S3SessionManager."""

import json
from unittest.mock import Mock

import boto3
import pytest
from botocore.config import Config as BotocoreConfig
from botocore.exceptions import ClientError
from moto import mock_aws

from strands.agent.conversation_manager.null_conversation_manager import NullConversationManager
from strands.session.s3_session_manager import S3SessionManager
from strands.types.content import ContentBlock
from strands.types.exceptions import SessionException
from strands.types.session import Session, SessionAgent, SessionMessage, SessionType


@pytest.fixture
def mocked_aws():
    """
    Mock all AWS interactions
    Requires you to create your own boto3 clients
    """
    with mock_aws():
        yield


@pytest.fixture(scope="function")
def s3_bucket(mocked_aws):
    """S3 bucket name for testing."""
    # Create the bucket
    s3_client = boto3.client("s3", region_name="us-west-2")
    s3_client.create_bucket(Bucket="test-session-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"})
    return "test-session-bucket"


@pytest.fixture
def s3_manager(mocked_aws, s3_bucket):
    """Create S3SessionManager with mocked S3."""
    yield S3SessionManager(session_id="test", bucket=s3_bucket, prefix="sessions/", region_name="us-west-2")


@pytest.fixture
def sample_session():
    """Create sample session for testing."""
    return Session(
        session_id="test-session-123",
        session_type=SessionType.AGENT,
    )


@pytest.fixture
def sample_agent():
    """Create sample agent for testing."""
    return SessionAgent(
        agent_id="test-agent-456",
        state={"key": "value"},
        conversation_manager_state=NullConversationManager().get_state(),
    )


@pytest.fixture
def sample_message():
    """Create sample message for testing."""
    return SessionMessage.from_message(
        message={
            "role": "user",
            "content": [ContentBlock(text="test_message")],
        },
        index=0,
    )


def test_init_s3_session_manager(mocked_aws, s3_bucket):
    session_manager = S3SessionManager(session_id="test", bucket=s3_bucket)
    assert "strands-agents" in session_manager.client.meta.config.user_agent_extra


def test_init_s3_session_manager_with_config(mocked_aws, s3_bucket):
    session_manager = S3SessionManager(session_id="test", bucket=s3_bucket, boto_client_config=BotocoreConfig())
    assert "strands-agents" in session_manager.client.meta.config.user_agent_extra


def test_init_s3_session_manager_with_existing_user_agent(mocked_aws, s3_bucket):
    session_manager = S3SessionManager(
        session_id="test", bucket=s3_bucket, boto_client_config=BotocoreConfig(user_agent_extra="test")
    )
    assert "strands-agents" in session_manager.client.meta.config.user_agent_extra


def test_create_session(s3_manager, sample_session):
    """Test creating a session in S3."""
    result = s3_manager.create_session(sample_session)

    assert result == sample_session

    # Verify S3 object created
    key = f"{s3_manager._get_session_path(sample_session.session_id)}session.json"
    response = s3_manager.client.get_object(Bucket=s3_manager.bucket, Key=key)
    data = json.loads(response["Body"].read().decode("utf-8"))

    assert data["session_id"] == sample_session.session_id
    assert data["session_type"] == sample_session.session_type


def test_create_session_already_exists(s3_manager, sample_session):
    """Test creating a session in S3."""
    s3_manager.create_session(sample_session)

    with pytest.raises(SessionException):
        s3_manager.create_session(sample_session)


def test_read_session(s3_manager, sample_session):
    """Test reading a session from S3."""
    # Create session first
    s3_manager.create_session(sample_session)

    # Read it back
    result = s3_manager.read_session(sample_session.session_id)

    assert result.session_id == sample_session.session_id
    assert result.session_type == sample_session.session_type


def test_read_nonexistent_session(s3_manager):
    """Test reading a session that doesn't exist in S3."""
    with mock_aws():
        result = s3_manager.read_session("nonexistent-session")
        assert result is None


def test_delete_session(s3_manager, sample_session):
    """Test deleting a session from S3."""
    # Create session first
    s3_manager.create_session(sample_session)

    # Verify session exists
    key = f"{s3_manager._get_session_path(sample_session.session_id)}session.json"
    s3_manager.client.head_object(Bucket=s3_manager.bucket, Key=key)

    # Delete session
    s3_manager.delete_session(sample_session.session_id)

    # Verify deletion
    with pytest.raises(ClientError) as excinfo:
        s3_manager.client.head_object(Bucket=s3_manager.bucket, Key=key)
    assert excinfo.value.response["Error"]["Code"] == "404"


def test_create_agent(s3_manager, sample_session, sample_agent):
    """Test creating an agent in S3."""
    # Create session first
    s3_manager.create_session(sample_session)

    # Create agent
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Verify S3 object created
    key = f"{s3_manager._get_agent_path(sample_session.session_id, sample_agent.agent_id)}agent.json"
    response = s3_manager.client.get_object(Bucket=s3_manager.bucket, Key=key)
    data = json.loads(response["Body"].read().decode("utf-8"))

    assert data["agent_id"] == sample_agent.agent_id
    assert data["state"] == sample_agent.state


def test_read_agent(s3_manager, sample_session, sample_agent):
    """Test reading an agent from S3."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Read agent
    result = s3_manager.read_agent(sample_session.session_id, sample_agent.agent_id)

    assert result.agent_id == sample_agent.agent_id
    assert result.state == sample_agent.state


def test_read_nonexistent_agent(s3_manager, sample_session, sample_agent):
    """Test reading an agent from S3."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    # Read agent
    result = s3_manager.read_agent(sample_session.session_id, "nonexistent_agent")

    assert result is None


def test_update_agent(s3_manager, sample_session, sample_agent):
    """Test updating an agent in S3."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Update agent
    sample_agent.state = {"updated": "value"}
    s3_manager.update_agent(sample_session.session_id, sample_agent)

    # Verify update
    result = s3_manager.read_agent(sample_session.session_id, sample_agent.agent_id)
    assert result.state == {"updated": "value"}


def test_update_nonexistent_agent(s3_manager, sample_session, sample_agent):
    """Test updating an agent in S3."""
    # Create session and agent
    s3_manager.create_session(sample_session)

    with pytest.raises(SessionException):
        s3_manager.update_agent(sample_session.session_id, sample_agent)


def test_create_message(s3_manager, sample_session, sample_agent, sample_message):
    """Test creating a message in S3."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Create message
    s3_manager.create_message(sample_session.session_id, sample_agent.agent_id, sample_message)

    # Verify S3 object created
    key = s3_manager._get_message_path(sample_session.session_id, sample_agent.agent_id, sample_message.message_id)
    response = s3_manager.client.get_object(Bucket=s3_manager.bucket, Key=key)
    data = json.loads(response["Body"].read().decode("utf-8"))

    assert data["message_id"] == sample_message.message_id


def test_read_message(s3_manager, sample_session, sample_agent, sample_message):
    """Test reading a message from S3."""
    # Create session, agent, and message
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)
    s3_manager.create_message(sample_session.session_id, sample_agent.agent_id, sample_message)

    # Read message
    result = s3_manager.read_message(sample_session.session_id, sample_agent.agent_id, sample_message.message_id)

    assert result.message_id == sample_message.message_id
    assert result.message["role"] == sample_message.message["role"]
    assert result.message["content"] == sample_message.message["content"]


def test_read_nonexistent_message(s3_manager, sample_session, sample_agent, sample_message):
    """Test reading a message from S3."""
    # Create session, agent, and message
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Read message
    result = s3_manager.read_message(sample_session.session_id, sample_agent.agent_id, 999)

    assert result is None


def test_list_messages_all(s3_manager, sample_session, sample_agent):
    """Test listing all messages from S3."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Create multiple messages
    messages = []
    for i in range(5):
        message = SessionMessage(
            {
                "role": "user",
                "content": [ContentBlock(text=f"Message {i}")],
            },
            i,
        )
        messages.append(message)
        s3_manager.create_message(sample_session.session_id, sample_agent.agent_id, message)

    # List all messages
    result = s3_manager.list_messages(sample_session.session_id, sample_agent.agent_id)

    assert len(result) == 5


def test_list_messages_with_pagination(s3_manager, sample_session, sample_agent):
    """Test listing messages with pagination in S3."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Create multiple messages
    for index in range(10):
        message = SessionMessage.from_message(
            message={
                "role": "user",
                "content": [ContentBlock(text="test_message")],
            },
            index=index,
        )
        s3_manager.create_message(sample_session.session_id, sample_agent.agent_id, message)

    # List with limit
    result = s3_manager.list_messages(sample_session.session_id, sample_agent.agent_id, limit=3)
    assert len(result) == 3

    # List with offset
    result = s3_manager.list_messages(sample_session.session_id, sample_agent.agent_id, offset=5)
    assert len(result) == 5


def test_update_message(s3_manager, sample_session, sample_agent, sample_message):
    """Test updating a message in S3."""
    # Create session, agent, and message
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)
    s3_manager.create_message(sample_session.session_id, sample_agent.agent_id, sample_message)

    # Update message
    sample_message.message["content"] = [ContentBlock(text="Updated content")]
    s3_manager.update_message(sample_session.session_id, sample_agent.agent_id, sample_message)

    # Verify update
    result = s3_manager.read_message(sample_session.session_id, sample_agent.agent_id, sample_message.message_id)
    assert result.message["content"][0]["text"] == "Updated content"


def test_update_nonexistent_message(s3_manager, sample_session, sample_agent, sample_message):
    """Test updating a message in S3."""
    # Create session, agent, and message
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Update message
    with pytest.raises(SessionException):
        s3_manager.update_message(sample_session.session_id, sample_agent.agent_id, sample_message)


@pytest.mark.parametrize(
    "session_id",
    [
        "a/../b",
        "a/b",
    ],
)
def test__get_session_path_invalid_session_id(session_id, s3_manager):
    with pytest.raises(ValueError, match=f"session_id={session_id} | id cannot contain path separators"):
        s3_manager._get_session_path(session_id)


@pytest.mark.parametrize(
    "agent_id",
    [
        "a/../b",
        "a/b",
    ],
)
def test__get_agent_path_invalid_agent_id(agent_id, s3_manager):
    with pytest.raises(ValueError, match=f"agent_id={agent_id} | id cannot contain path separators"):
        s3_manager._get_agent_path("session1", agent_id)


@pytest.mark.parametrize(
    "message_id",
    [
        "../../../secret",
        "../../attack",
        "../escape",
        "path/traversal",
        "not_an_int",
        None,
        [],
    ],
)
def test__get_message_path_invalid_message_id(message_id, s3_manager):
    """Test that message_id that is not an integer raises ValueError."""
    with pytest.raises(ValueError, match=r"message_id=<.*> \| message id must be an integer"):
        s3_manager._get_message_path("session1", "agent1", message_id)


@pytest.fixture
def mock_multi_agent():
    """Create mock multi-agent for testing."""

    mock = Mock()
    mock.id = "test-multi-agent"
    mock.state = {"key": "value"}
    mock.serialize_state.return_value = {"id": "test-multi-agent", "state": {"key": "value"}}
    return mock


def test_create_multi_agent(s3_manager, sample_session, mock_multi_agent):
    """Test creating multi-agent state in S3."""
    s3_manager.create_session(sample_session)
    s3_manager.create_multi_agent(sample_session.session_id, mock_multi_agent)

    # Verify S3 object created
    key = f"{s3_manager._get_multi_agent_path(sample_session.session_id, mock_multi_agent.id)}multi_agent.json"
    response = s3_manager.client.get_object(Bucket=s3_manager.bucket, Key=key)
    data = json.loads(response["Body"].read().decode("utf-8"))

    assert data["id"] == mock_multi_agent.id
    assert data["state"] == mock_multi_agent.state


def test_read_multi_agent(s3_manager, sample_session, mock_multi_agent):
    """Test reading multi-agent state from S3."""
    # Create session and multi-agent
    s3_manager.create_session(sample_session)
    s3_manager.create_multi_agent(sample_session.session_id, mock_multi_agent)

    # Read multi-agent
    result = s3_manager.read_multi_agent(sample_session.session_id, mock_multi_agent.id)

    assert result["id"] == mock_multi_agent.id
    assert result["state"] == mock_multi_agent.state


def test_read_nonexistent_multi_agent(s3_manager, sample_session):
    """Test reading multi-agent state that doesn't exist."""
    s3_manager.create_session(sample_session)
    result = s3_manager.read_multi_agent(sample_session.session_id, "nonexistent")
    assert result is None


def test_update_multi_agent(s3_manager, sample_session, mock_multi_agent):
    """Test updating multi-agent state in S3."""
    # Create session and multi-agent
    s3_manager.create_session(sample_session)
    s3_manager.create_multi_agent(sample_session.session_id, mock_multi_agent)

    updated_mock = Mock()
    updated_mock.id = mock_multi_agent.id
    updated_mock.serialize_state.return_value = {"id": mock_multi_agent.id, "state": {"updated": "value"}}
    s3_manager.update_multi_agent(sample_session.session_id, updated_mock)

    # Verify update
    result = s3_manager.read_multi_agent(sample_session.session_id, mock_multi_agent.id)
    assert result["state"] == {"updated": "value"}


def test_update_nonexistent_multi_agent(s3_manager, sample_session):
    """Test updating multi-agent state that doesn't exist."""
    # Create session
    s3_manager.create_session(sample_session)

    nonexistent_mock = Mock()
    nonexistent_mock.id = "nonexistent"
    with pytest.raises(SessionException):
        s3_manager.update_multi_agent(sample_session.session_id, nonexistent_mock)


def test_init_with_custom_s3_client(mocked_aws, s3_bucket):
    """Test that S3SessionManager can accept a custom S3 client."""
    # Create a custom S3 client
    custom_client = boto3.client("s3", region_name="us-east-1")

    # Initialize manager with custom client
    manager = S3SessionManager(session_id="test", bucket=s3_bucket, s3_client=custom_client)

    # Verify the custom client is used
    assert manager.client is custom_client


def test_init_with_custom_s3_client_ignores_other_params(mocked_aws, s3_bucket):
    """Test that when s3_client is provided, other boto params are ignored."""
    # Create a custom S3 client
    custom_client = boto3.client("s3", region_name="us-east-1")

    # These params should be ignored when s3_client is provided
    manager = S3SessionManager(
        session_id="test",
        bucket=s3_bucket,
        s3_client=custom_client,
        region_name="us-west-2",  # Should be ignored
        boto_client_config=BotocoreConfig(user_agent_extra="test"),  # Should be ignored
    )

    # Verify the custom client is used (not a new one from the ignored params)
    assert manager.client is custom_client


def test_set_session_id(s3_manager, sample_session):
    """Test updating session_id on an existing manager."""
    # Create initial session
    s3_manager.create_session(sample_session)

    # Change to a different session_id
    new_session_id = "new-session-456"
    s3_manager.set_session_id(new_session_id)

    # Verify session_id was updated
    assert s3_manager.session_id == new_session_id

    # Verify we can now work with the new session
    new_session = Session(session_id=new_session_id, session_type=SessionType.AGENT)
    s3_manager.create_session(new_session)

    # Read back the new session
    result = s3_manager.read_session(new_session_id)
    assert result.session_id == new_session_id


def test_set_session_id_singleton_pattern(mocked_aws):
    """Test using S3SessionManager as a singleton with multiple session IDs."""
    # Create a dedicated bucket for this test to avoid state sharing
    import uuid

    s3_client = boto3.client("s3", region_name="us-west-2")
    test_bucket = f"test-singleton-bucket-{uuid.uuid4().hex[:8]}"
    s3_client.create_bucket(Bucket=test_bucket, CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

    # Create a single manager instance and manually create sessions
    manager = S3SessionManager(session_id="dummy-initial", bucket=test_bucket, region_name="us-west-2")

    # Create first session manually (bypassing RepositorySessionManager auto-creation)
    session1 = Session(session_id="singleton-session-1", session_type=SessionType.AGENT)
    session1_key = f"{manager._get_session_path('singleton-session-1')}session.json"
    manager._write_s3_object(session1_key, session1.to_dict())

    # Create second session manually
    session2 = Session(session_id="singleton-session-2", session_type=SessionType.AGENT)
    session2_key = f"{manager._get_session_path('singleton-session-2')}session.json"
    manager._write_s3_object(session2_key, session2.to_dict())

    # Create third session manually
    session3 = Session(session_id="singleton-session-3", session_type=SessionType.AGENT)
    session3_key = f"{manager._get_session_path('singleton-session-3')}session.json"
    manager._write_s3_object(session3_key, session3.to_dict())

    # Now test switching between sessions using set_session_id
    manager.set_session_id("singleton-session-1")
    assert manager.read_session("singleton-session-1").session_id == "singleton-session-1"

    manager.set_session_id("singleton-session-2")
    assert manager.read_session("singleton-session-2").session_id == "singleton-session-2"

    manager.set_session_id("singleton-session-3")
    assert manager.read_session("singleton-session-3").session_id == "singleton-session-3"

    # Verify the manager's session_id was updated correctly
    assert manager.session_id == "singleton-session-3"


def test_set_session_id_invalid(s3_manager):
    """Test that set_session_id validates the new session_id."""
    # Try to set an invalid session_id with path separators
    with pytest.raises(ValueError, match="id cannot contain path separators"):
        s3_manager.set_session_id("invalid/session/id")


def test_list_messages_parallel_order_preserved(s3_manager, sample_session, sample_agent):
    """Test that parallel message retrieval preserves message order."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Create 100 messages with distinct content
    expected_order = []
    for i in range(100):
        message = SessionMessage.from_message(
            message={
                "role": "user",
                "content": [ContentBlock(text=f"Message {i}")],
            },
            index=i,
        )
        expected_order.append(f"Message {i}")
        s3_manager.create_message(sample_session.session_id, sample_agent.agent_id, message)

    # List all messages
    result = s3_manager.list_messages(sample_session.session_id, sample_agent.agent_id)

    # Verify order is preserved
    assert len(result) == 100
    for i, message in enumerate(result):
        assert message.message["content"][0]["text"] == expected_order[i]


def test_list_messages_parallel_with_pagination(s3_manager, sample_session, sample_agent):
    """Test that parallel message retrieval works correctly with pagination."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # Create 50 messages
    for i in range(50):
        message = SessionMessage.from_message(
            message={
                "role": "user",
                "content": [ContentBlock(text=f"Message {i}")],
            },
            index=i,
        )
        s3_manager.create_message(sample_session.session_id, sample_agent.agent_id, message)

    # Test limit
    result = s3_manager.list_messages(sample_session.session_id, sample_agent.agent_id, limit=10)
    assert len(result) == 10
    assert result[0].message["content"][0]["text"] == "Message 0"
    assert result[9].message["content"][0]["text"] == "Message 9"

    # Test offset
    result = s3_manager.list_messages(sample_session.session_id, sample_agent.agent_id, offset=40, limit=10)
    assert len(result) == 10
    assert result[0].message["content"][0]["text"] == "Message 40"
    assert result[9].message["content"][0]["text"] == "Message 49"


def test_list_messages_empty(s3_manager, sample_session, sample_agent):
    """Test listing messages when there are no messages."""
    # Create session and agent
    s3_manager.create_session(sample_session)
    s3_manager.create_agent(sample_session.session_id, sample_agent)

    # List messages (should be empty)
    result = s3_manager.list_messages(sample_session.session_id, sample_agent.agent_id)
    assert len(result) == 0

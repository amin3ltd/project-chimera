"""Test for Skills Interface - This test SHOULD fail initially."""

def test_skill_input_contract():
    """Asserts that skills modules accept the correct parameters."""
    from skills import SkillRegistry
    
    # This should fail until SkillRegistry is implemented
    registry = SkillRegistry()
    
    # Test that we can register a skill
    assert hasattr(registry, 'register')
    assert hasattr(registry, 'get')


def test_download_youtube_skill():
    """Test that download_youtube skill accepts correct parameters."""
    from skills.skill_download_youtube import DownloadYoutubeSkill
    
    skill = DownloadYoutubeSkill()
    
    # Should have an execute method
    assert hasattr(skill, 'execute')
    
    # Execute should accept url parameter
    import inspect
    sig = inspect.signature(skill.execute)
    params = list(sig.parameters.keys())
    
    assert 'url' in params
    assert 'output_path' in params


def test_transcribe_audio_skill():
    """Test that transcribe_audio skill accepts correct parameters."""
    from skills.skill_transcribe_audio import TranscribeAudioSkill
    
    skill = TranscribeAudioSkill()
    
    assert hasattr(skill, 'execute')
    
    import inspect
    sig = inspect.signature(skill.execute)
    params = list(sig.parameters.keys())
    
    assert 'audio_path' in params


def test_analyze_trends_skill():
    """Test that analyze_trends skill accepts correct parameters."""
    from skills.skill_analyze_trends import AnalyzeTrendsSkill
    
    skill = AnalyzeTrendsSkill()
    
    assert hasattr(skill, 'execute')
    
    import inspect
    sig = inspect.signature(skill.execute)
    params = list(sig.parameters.keys())
    
    assert 'content' in params
    assert 'platform' in params


def test_generate_image_skill():
    """Test that generate_image skill accepts correct parameters."""
    from skills.skill_generate_image import GenerateImageSkill
    
    skill = GenerateImageSkill()
    
    assert hasattr(skill, 'execute')
    
    import inspect
    sig = inspect.signature(skill.execute)
    params = list(sig.parameters.keys())
    
    assert 'prompt' in params


def test_post_content_skill():
    """Test that post_content skill accepts correct parameters."""
    from skills.skill_post_content import PostContentSkill
    
    skill = PostContentSkill()
    
    assert hasattr(skill, 'execute')
    
    import inspect
    sig = inspect.signature(skill.execute)
    params = list(sig.parameters.keys())
    
    assert 'platform' in params
    assert 'text_content' in params

from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    """YouTube URL에서 Video ID를 추출합니다.
    
    Args:
        url: YouTube URL (검증된 URL)
        
    Returns:
        str: Video ID
        
    Raises:
        ValueError: Video ID를 추출할 수 없는 경우
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    video_id_list = query_params.get('v')
    if not video_id_list:
        raise ValueError("Video ID를 추출할 수 없습니다.")
    
    video_id = video_id_list[0]
    return video_id
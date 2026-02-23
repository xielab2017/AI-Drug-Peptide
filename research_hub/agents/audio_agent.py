"""
Audio Agent - 音频生成代理
将文本转换为语音播客
"""

import os
import tempfile
from typing import Optional
from enum import Enum


class TTSEngine(Enum):
    """TTS 引擎"""
    GTTS = "gtts"           # Google TTS (免费)
    ELEVENLABS = "elevenlabs"  # ElevenLabs (高质量)
    SAG = "sag"             # OpenClaw 内置 TTS


class AudioAgent:
    """音频生成代理"""
    
    def __init__(
        self, 
        engine: str = "gtts",
        output_dir: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None
    ):
        """
        初始化音频代理
        
        Args:
            engine: TTS 引擎 (gtts, elevenlabs, sag)
            output_dir: 输出目录
            elevenlabs_api_key: ElevenLabs API 密钥
        """
        self.engine = TTSEngine(engine.lower())
        self.output_dir = output_dir or tempfile.gettempdir()
        self.elevenlabs_api_key = elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")
        
        # 检查依赖
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查依赖是否安装"""
        if self.engine == TTSEngine.GTTS:
            try:
                import gtts
                self.gtts = __import__('gtts')
            except ImportError:
                raise ImportError("gTTS not installed. Run: pip install gtts")
    
    def text_to_audio(
        self, 
        text: str, 
        filename: str = "output.mp3",
        language: str = "en",
        **kwargs
    ) -> str:
        """
        文本转音频
        
        Args:
            text: 输入文本
            filename: 输出文件名
            language: 语言代码
            **kwargs: 其他参数
            
        Returns:
            音频文件路径
        """
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, filename)
        
        if self.engine == TTSEngine.GTTS:
            return self._gtts_convert(text, output_path, language)
        elif self.engine == TTSEngine.ELEVENLABS:
            return self._elevenlabs_convert(text, output_path, **kwargs)
        elif self.engine == TTSEngine.SAG:
            return self._sag_convert(text, output_path, **kwargs)
        else:
            raise ValueError(f"Unknown engine: {self.engine}")
    
    def _gtts_convert(self, text: str, output_path: str, language: str) -> str:
        """
        使用 gTTS 转换
        
        Args:
            text: 文本
            output_path: 输出路径
            language: 语言
            
        Returns:
            输出路径
        """
        from gtts import gTTS
        
        # 截断过长文本（gTTS 限制）
        text = text[:5000]
        
        tts = gTTS(text=text, lang=language)
        tts.save(output_path)
        
        return output_path
    
    def _elevenlabs_convert(
        self, 
        text: str, 
        output_path: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",
        **kwargs
    ) -> str:
        """
        使用 ElevenLabs 转换
        
        Args:
            text: 文本
            output_path: 输出路径
            voice_id: 语音 ID
            **kwargs: 其他参数
            
        Returns:
            输出路径
        """
        import requests
        
        if not self.elevenlabs_api_key:
            raise ValueError("ElevenLabs API key not set")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": kwargs.get("voice_settings", {
                "stability": 0.5,
                "similarity_boost": 0.5
            })
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.text}")
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
    
    def _sag_convert(
        self, 
        text: str, 
        output_path: str,
        voice: str = "default",
        **kwargs
    ) -> str:
        """
        使用 OpenClaw 内置 TTS (sag)
        
        注意：实际使用需要在 OpenClaw 中调用 TTS 工具
        
        Args:
            text: 文本
            output_path: 输出路径
            voice: 语音
            **kwargs: 其他参数
            
        Returns:
            输出路径
        """
        # 这是一个占位实现
        # 实际使用时，OpenClaw 会通过 tts 工具调用
        raise NotImplementedError(
            "SAG TTS requires OpenClaw runtime. "
            "Use tts tool directly in OpenClaw."
        )
    
    def text_to_audio_segments(
        self, 
        text: str, 
        segment_length: int = 1500,
        language: str = "en",
        **kwargs
    ) -> list:
        """
        将长文本分段转换为音频
        
        Args:
            text: 文本
            segment_length: 每段长度
            language: 语言
            **kwargs: 其他参数
            
        Returns:
            音频文件路径列表
        """
        # 分割文本（按句子）
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        segments = []
        current_segment = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > segment_length and current_segment:
                segments.append(' '.join(current_segment))
                current_segment = [sentence]
                current_length = len(sentence)
            else:
                current_segment.append(sentence)
                current_length += len(sentence)
        
        if current_segment:
            segments.append(' '.join(current_segment))
        
        # 转换每个段落
        output_paths = []
        base_name = kwargs.get('base_name', 'segment')
        
        for i, segment in enumerate(segments):
            filename = f"{base_name}_{i+1}.mp3"
            path = self.text_to_audio(segment, filename, language, **kwargs)
            output_paths.append(path)
        
        return output_paths
    
    def generate_podcast(
        self, 
        text: str, 
        output_path: str = None,
        intro: str = None,
        outro: str = None,
        language: str = "en",
        **kwargs
    ) -> str:
        """
        生成播客风格的音频
        
        Args:
            text: 主要内容文本
            output_path: 输出路径
            intro: 开场白
            outro: 结束语
            language: 语言
            
        Returns:
            音频文件路径
        """
        # 构建完整文本
        full_text = ""
        
        if intro:
            full_text += intro + " "
        
        full_text += text
        
        if outro:
            full_text += " " + outro
        
        # 转换
        if output_path is None:
            import time
            output_path = os.path.join(self.output_dir, f"podcast_{int(time.time())}.mp3")
        
        return self.text_to_audio(full_text, output_path, language, **kwargs)
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        获取音频文件信息
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            音频信息
        """
        import os
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        stat = os.stat(audio_path)
        
        info = {
            "path": audio_path,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2)
        }
        
        # 尝试获取时长
        try:
            from mutagen.mp3 import MP3
            audio = MP3(audio_path)
            info["duration_seconds"] = audio.info.length
        except:
            pass
        
        return info


# CLI 测试
if __name__ == "__main__":
    # 使用示例
    
    # 1. 使用 gTTS
    agent = AudioAgent(engine="gtts", output_dir="/tmp/research-hub-audio")
    
    text = """
    This is a test of the text to speech system. 
    ResearchHub can convert research paper summaries into audio podcasts.
    """
    
    output = agent.text_to_audio(text, "test.mp3", language="en")
    print(f"Audio saved to: {output}")
    
    # 2. 获取音频信息
    info = agent.get_audio_info(output)
    print(f"Audio info: {info}")

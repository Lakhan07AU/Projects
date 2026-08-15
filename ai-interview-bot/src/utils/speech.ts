/**
 * Web Speech API helper for speech synthesis (TTS) and voice recognition (STT).
 * Works reliably in modern browsers with graceful fallback.
 */

// Invalidate pending TTS callbacks whenever speech is cancelled/restarted
let speechToken = 0;

// Voice synthesizer
export function speakText(text: string, voiceName?: string, onEnd?: () => void): void {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    onEnd?.();
    return;
  }

  // Cancel any ongoing speech
  window.speechSynthesis.cancel();

  // Strip code blocks or excessive markdown for clean speech
  const cleanText = text
    .replace(/```[\s\S]*?```/g, 'Code example omitted.')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/[*#_~]/g, '')
    .trim();

  if (!cleanText) {
    onEnd?.();
    return;
  }

  const token = ++speechToken;
  const utterance = new SpeechSynthesisUtterance(cleanText);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;

  const voices = window.speechSynthesis.getVoices();
  if (voiceName) {
    const chosen = voices.find(v => v.name === voiceName);
    if (chosen) {
      utterance.voice = chosen;
    }
  } else if (voices.length > 0) {
    // Prefer natural English voices
    const englishVoice = voices.find(v => 
      (v.lang.includes('en-US') || v.lang.includes('en-GB')) && 
      (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Samantha') || v.name.includes('Daniel'))
    ) || voices.find(v => v.lang.startsWith('en'));

    if (englishVoice) {
      utterance.voice = englishVoice;
    }
  }

  utterance.onend = () => {
    if (token === speechToken) onEnd?.();
  };
  utterance.onerror = () => {
    if (token === speechToken) onEnd?.();
  };

  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking(): void {
  // Invalidate any pending onEnd callbacks from previous utterances
  speechToken++;
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
}

// Voice Recognition (Speech to Text)
export interface SpeechRecognitionListener {
  onTranscript: (text: string, isFinal: boolean) => void;
  onError: (error: string) => void;
  onEnd: () => void;
}

export function getSpeechRecognitionSupport(): { supported: boolean; preferred: boolean } {
  if (typeof window === 'undefined') {
    return { supported: false, preferred: false };
  }
  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  return {
    supported: Boolean(SpeechRecognition),
    preferred: /chrome|edg|edge/i.test(navigator.userAgent),
  };
}

export function getFriendlyMicError(error: string): string {
  switch (error) {
    case 'not-allowed':
    case 'service-not-allowed':
      return 'Microphone access was denied. Allow microphone permission (lock icon in the address bar) and try again.';
    case 'network':
      return 'Speech recognition could not reach the network. Check your internet connection and try again.';
    case 'audio-capture':
      return 'No microphone was detected. Connect a microphone, then try again.';
    case 'no-speech':
      return 'No speech was detected. Speak clearly into your microphone and try again.';
    case 'aborted':
      return '';
    default:
      return `Voice input issue (${error}). You can type your answer directly.`;
  }
}

export function createSpeechRecognizer(listener: SpeechRecognitionListener) {
  if (typeof window === 'undefined') return null;

  const SpeechRecognition = 
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

  if (!SpeechRecognition) {
    return null;
  }

  try {
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      if (final) {
        listener.onTranscript(final.trim(), true);
      } else if (interim) {
        listener.onTranscript(interim, false);
      }
    };

    recognition.onerror = (event: any) => {
      listener.onError(event.error || 'Speech recognition error');
    };

    recognition.onend = () => {
      listener.onEnd();
    };

    return recognition;
  } catch (e) {
    console.warn('Speech recognition setup failed:', e);
    return null;
  }
}

/**
 * Audio recording fallback used when the browser's built-in speech service
 * is unreachable (e.g. 'network' errors). Uses MediaRecorder in the browser,
 * then the returned handle's stop() yields a Blob for server transcription.
 */
export interface AudioRecorderHandle {
  stop: () => Promise<{ blob: Blob; mimeType: string }>;
}

export function isAudioRecordingSupported(): boolean {
  return (
    typeof window !== 'undefined' &&
    !!navigator.mediaDevices &&
    typeof navigator.mediaDevices.getUserMedia === 'function' &&
    typeof (window as any).MediaRecorder === 'function'
  );
}

function pickMimeType(): string | undefined {
  const candidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
  for (const c of candidates) {
    try {
      if ((window as any).MediaRecorder.isTypeSupported(c)) return c;
    } catch {
      // ignore
    }
  }
  return undefined;
}

export async function createAudioRecorder(): Promise<AudioRecorderHandle | null> {
  if (!isAudioRecordingSupported()) return null;

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mimeType = pickMimeType();
  const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  const chunks: Blob[] = [];

  recorder.ondataavailable = (e) => {
    if (e.data.size > 0) chunks.push(e.data);
  };

  recorder.start(250);

  return {
    stop: () =>
      new Promise<{ blob: Blob; mimeType: string }>((resolve, reject) => {
        const done = () => {
          stream.getTracks().forEach((t) => t.stop());
          const finalMime = mimeType || recorder.mimeType || 'audio/webm';
          resolve({ blob: new Blob(chunks, { type: finalMime }), mimeType: finalMime });
        };
        recorder.onstop = done;
        recorder.onerror = (e) => {
          stream.getTracks().forEach((t) => t.stop());
          reject(e);
        };
        try {
          recorder.stop();
        } catch (e) {
          done();
        }
      }),
  };
}

/**
 * Upload a recorded audio blob to the server, which transcribes it via Groq
 * Whisper. Returns the transcribed text.
 */
export async function transcribeAudio(blob: Blob, mimeType: string): Promise<string> {
  const res = await fetch('/api/speech/transcribe', {
    method: 'POST',
    headers: { 'Content-Type': mimeType },
    body: blob,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.error || 'Transcription failed. Please try again or type your answer.');
  }
  return data.text || '';
}


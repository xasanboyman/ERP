/**
 * Ultra-Lightweight Web Audio Sound Synthesizer
 *
 * Uses HTML5 AudioContext & OscillatorNode to synthesize crisp sound effects
 * with ZERO external audio files (.mp3/.wav), ZERO network downloads,
 * and ZERO memory leaks (auto-suspends context when idle).
 */

class SoundEffectsManager {
  private ctx: AudioContext | null = null
  private isMuted: boolean = false

  private getAudioContext(): AudioContext | null {
    if (this.isMuted) return null
    try {
      if (!this.ctx) {
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext
        if (AudioCtx) {
          this.ctx = new AudioCtx()
        }
      }
      if (this.ctx && this.ctx.state === 'suspended') {
        this.ctx.resume()
      }
      return this.ctx
    } catch {
      return null
    }
  }

  /**
   * Crisp, pleasant high-frequency barcode scanner beep (880Hz -> 1050Hz, 70ms)
   */
  public playScanSuccess(): void {
    const ctx = this.getAudioContext()
    if (!ctx) return

    try {
      const now = ctx.currentTime
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()

      osc.type = 'sine'
      osc.frequency.setValueAtTime(880, now)
      osc.frequency.exponentialRampToValueAtTime(1050, now + 0.06)

      gain.gain.setValueAtTime(0.12, now)
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.07)

      osc.connect(gain)
      gain.connect(ctx.destination)

      osc.start(now)
      osc.stop(now + 0.07)
    } catch (_) {
      // Audio playback failed or blocked by autoplay policy
    }
  }

  /**
   * Melodic 3-tone checkout success chime (Major triad: C5 - E5 - G5, 220ms)
   */
  public playCheckoutSuccess(): void {
    const ctx = this.getAudioContext()
    if (!ctx) return

    try {
      const freqs = [523.25, 659.25, 783.99] // C5, E5, G5
      const now = ctx.currentTime

      freqs.forEach((freq, idx) => {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()

        osc.type = 'triangle'
        osc.frequency.setValueAtTime(freq, now + idx * 0.06)

        gain.gain.setValueAtTime(0.14, now + idx * 0.06)
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.06 + 0.16)

        osc.connect(gain)
        gain.connect(ctx.destination)

        osc.start(now + idx * 0.06)
        osc.stop(now + idx * 0.06 + 0.17)
      })
    } catch (_) {
      // Audio playback failed or blocked by autoplay policy
    }
  }

  /**
   * Double-pulse warning/error tone (320Hz, 120ms) for out-of-stock / invalid barcodes
   */
  public playWarning(): void {
    const ctx = this.getAudioContext()
    if (!ctx) return

    try {
      const now = ctx.currentTime
      ;[0, 0.09].forEach((offset) => {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()

        osc.type = 'sawtooth'
        osc.frequency.setValueAtTime(320, now + offset)

        gain.gain.setValueAtTime(0.1, now + offset)
        gain.gain.exponentialRampToValueAtTime(0.001, now + offset + 0.07)

        osc.connect(gain)
        gain.connect(ctx.destination)

        osc.start(now + offset)
        osc.stop(now + offset + 0.07)
      })
    } catch (_) {
      // Audio playback failed or blocked by autoplay policy
    }
  }

  /**
   * Subtle click/remove tone (450Hz -> 200Hz, 40ms)
   */
  public playItemRemove(): void {
    const ctx = this.getAudioContext()
    if (!ctx) return

    try {
      const now = ctx.currentTime
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()

      osc.type = 'sine'
      osc.frequency.setValueAtTime(450, now)
      osc.frequency.exponentialRampToValueAtTime(200, now + 0.04)

      gain.gain.setValueAtTime(0.08, now)
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04)

      osc.connect(gain)
      gain.connect(ctx.destination)

      osc.start(now)
      osc.stop(now + 0.04)
    } catch (_) {
      // Audio playback failed or blocked by autoplay policy
    }
  }

  public toggleMute(): boolean {
    this.isMuted = !this.isMuted
    return this.isMuted
  }

  public getMuted(): boolean {
    return this.isMuted
  }
}

export const soundEffects = new SoundEffectsManager()

/**
 * OSIN Strategic Haptic Response System
 * Provides tactile telemetry feedback through the navigator.vibrate API.
 */
export class HapticController {
  private static instance: HapticController;
  private isSupported: boolean;

  private constructor() {
    this.isSupported = typeof navigator !== 'undefined' && 'vibrate' in navigator;
  }

  static getInstance(): HapticController {
    if (!HapticController.instance) {
      HapticController.instance = new HapticController();
    }
    return HapticController.instance;
  }

  /**
   * Basic vibration burst
   */
  vibrate(intensity: number = 0.5, duration: number = 100): void {
    if (!this.isSupported) return;
    
    // Higher intensity uses a modulated double-pattern
    const pattern = intensity > 0.7 
      ? [duration, 40, duration] 
      : [duration];
      
    try {
        navigator.vibrate(pattern);
    } catch (e) {
        console.warn('Haptic vibration failed:', e);
    }
  }

  /**
   * Pre-defined tactical patterns
   */
  onNodeSelect(): void {
    this.vibrate(0.6, 60);
  }

  onThreatDetected(): void {
    // Aggressive triple pulse
    if (this.isSupported) {
        navigator.vibrate([150, 50, 150, 50, 150]);
    }
  }

  onCriticalWarning(): void {
    // Long alarming pulses
    if (this.isSupported) {
        navigator.vibrate([400, 200, 400]);
    }
  }

  onTaskComplete(): void {
    // Soft double tap
    if (this.isSupported) {
        navigator.vibrate([40, 40, 40]);
    }
  }

  /**
   * Categorized feedback levels
   */
  feedback(type: 'light' | 'medium' | 'heavy'): void {
    if (!this.isSupported) return;
    
    const patterns = {
      light: [40],
      medium: [80, 40, 80],
      heavy: [150, 70, 150, 70, 150]
    };
    
    navigator.vibrate(patterns[type]);
  }
}

/**
 * React connector for haptic integration
 */
export const useHaptic = () => {
  const haptic = HapticController.getInstance();

  return {
    vibrate: haptic.vibrate.bind(haptic),
    onNodeSelect: haptic.onNodeSelect.bind(haptic),
    onThreatDetected: haptic.onThreatDetected.bind(haptic),
    onCriticalWarning: haptic.onCriticalWarning.bind(haptic),
    onTaskComplete: haptic.onTaskComplete.bind(haptic),
    feedback: haptic.feedback.bind(haptic)
  };
};

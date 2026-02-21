/**
 * Frontend Logger - Structured JSON logging to backend
 */

export class Logger {
  constructor(service = 'frontend') {
    this.service = service;
    this.buffer = [];
    this.bufferSize = 10;
  }

  log(level, message, context = {}) {
    const entry = {
      timestamp: new Date().toISOString(),
      level,
      service: this.service,
      message,
      ...context,
    };

    console.log(JSON.stringify(entry));
    this.buffer.push(entry);

    if (this.buffer.length >= this.bufferSize) {
      this.flush();
    }
  }

  error(message, context) {
    this.log('ERROR', message, context);
  }

  warn(message, context) {
    this.log('WARN', message, context);
  }

  info(message, context) {
    this.log('INFO', message, context);
  }

  debug(message, context) {
    this.log('DEBUG', message, context);
  }

  async flush() {
    if (this.buffer.length === 0) return;

    const logsToSend = [...this.buffer];
    this.buffer = [];

    try {
      await fetch('/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logsToSend),
      });
    } catch (error) {
      console.error('Failed to send logs:', error);
    }
  }
}

// Global instance
export const logger = new Logger('frontend');

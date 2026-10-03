'use client';

const BASE_URL = 'http://localhost:8000';

class ApiClient {
  private getSessionId(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('inferexa_session_id');
    }
    return null;
  }

  private getHeaders(contentType: string | null = 'application/json'): Headers {
    const headers = new Headers();
    if (contentType) {
      headers.append('Content-Type', contentType);
    }
    const sessionId = this.getSessionId();
    if (sessionId) {
      headers.append('X-Session-ID', sessionId);
    }
    return headers;
  }

  async request<T>(path: string, options: RequestInit): Promise<T> {
    const url = `${BASE_URL}${path}`;
    const response = await fetch(url, options);

    if (!response.ok) {
      let errorMsg = 'An error occurred during request execution.';
      try {
        const errJson = await response.json();
        errorMsg = errJson.detail || errorMsg;
      } catch (_) {
        // Fallback to text
        const text = await response.text();
        if (text) errorMsg = text;
      }
      throw new Error(errorMsg);
    }

    // Handle file downloads/blobs
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/pdf')) {
      return response.blob() as unknown as T;
    }

    try {
      return await response.json();
    } catch (_) {
      return {} as T;
    }
  }

  async get<T>(path: string): Promise<T> {
    return this.request<T>(path, {
      method: 'GET',
      headers: this.getHeaders(),
    });
  }

  async post<T>(path: string, body: any): Promise<T> {
    return this.request<T>(path, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
  }

  async put<T>(path: string, body: any): Promise<T> {
    return this.request<T>(path, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(body),
    });
  }

  async delete<T>(path: string): Promise<T> {
    return this.request<T>(path, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
  }

  async upload<T>(path: string, file: File): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<T>(path, {
      method: 'POST',
      headers: this.getHeaders(null), // fetch will auto set multipart boundary
      body: formData,
    });
  }
}

export const api = new ApiClient();

import { Injectable } from '@angular/core';
import { Message } from '../interfaces/message';
import { BehaviorSubject, Subject, firstValueFrom } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messageSubject = new Subject<Message>();
  private loadingSubject = new BehaviorSubject<boolean>(false);
  private sessionId: string | null = null;

  messages$ = this.messageSubject.asObservable();
  loading$ = this.loadingSubject.asObservable();

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {
    this.sessionId = localStorage.getItem('chatSessionId');
  }

  async initializeSession(): Promise<Message[]> {
    if (!this.sessionId) {
      // Crear nueva sesión
      const response = await firstValueFrom(
        this.http.post<{messages: Message[], sessionId: string}>(`${this.apiUrl}/init-session`, {})
      );
      this.sessionId = response.sessionId;
      localStorage.setItem('chatSessionId', this.sessionId);

      // Retornar los mensajes iniciales
      return response.messages;
    } else {
      // Cargar mensajes existentes
      const response = await firstValueFrom(
        this.http.get<{messages: Message[]}>(`${this.apiUrl}/messages/${this.sessionId}`)
      );

      // Retornar los mensajes existentes
      return response.messages;
    }
  }

  sendMessage(message: Message) {
    // Emitir el mensaje del usuario inmediatamente
    this.messageSubject.next(message);

    // Indicar que estamos cargando
    this.loadingSubject.next(true);

    const payload = {
      content: message.content,
      type: 'Human',
      sessionId: this.sessionId
    };

    this.http.post<{messages: Message[], sessionId: string}>(`${this.apiUrl}/chat`, payload)
      .subscribe({
        next: (response) => {
          this.sessionId = response.sessionId;
          localStorage.setItem('chatSessionId', this.sessionId);

          // Emitir solo la respuesta del AI
          response.messages.forEach(msg => {
            if (msg.type === 'AI') {
              this.messageSubject.next(msg);
              console.log('AI:', msg.content);
            }
          });
          this.loadingSubject.next(false);
        },
        error: (error) => {
          console.error('Error:', error);
          this.loadingSubject.next(false);
        }
      });
  }
}

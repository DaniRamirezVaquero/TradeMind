import { Injectable } from '@angular/core';
import { Message } from '../interfaces/message';
import { BehaviorSubject, Subject, firstValueFrom } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messageSubject = new Subject<Message>();
  private toolResultSubject = new Subject<Message>();
  private loadingSubject = new BehaviorSubject<boolean>(false);
  private sessionId: string | null = null;

  messages$ = this.messageSubject.asObservable();
  toolResults$ = this.toolResultSubject.asObservable();
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
      //TODO Gestionar de manera correcta el error en caso de que la sesión no exista
      try {
        // Cargar mensajes existentes
        const response = await firstValueFrom(
          this.http.get<{messages: Message[]}>(`${this.apiUrl}/messages/${this.sessionId}`)
        );
        console.log('Existing messages:', response.messages);
        // Retornar los mensajes existentes
        return response.messages;
      } catch (error) {
        // Si hay error, crear nueva sesión
        localStorage.removeItem('chatSessionId');
        this.sessionId = null;
        return this.initializeSession();
      }
    }
  }

  sendMessage(message: Message) {
    // Emitir el mensaje del usuario inmediatamente
    this.messageSubject.next(message);
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

          // Encontrar el último mensaje de AI
          const lastAIMessage = [...response.messages]
            .reverse()
            .find(msg => msg.type === 'AI');

          // Encontrar el último mensaje de tool_result
          const lastToolResult = [...response.messages]
            .reverse()
            .find(msg => msg.type === 'tool_result');

          // Emitir el último mensaje de AI si existe
          if (lastAIMessage) {
            this.messageSubject.next(lastAIMessage);
            console.log('Last AI message:', lastAIMessage);
          }

          // Emitir el último mensaje de tool_result si existe
          if (lastToolResult) {
            this.toolResultSubject.next(lastToolResult);
            console.log('Last tool_result:', lastToolResult);}

          this.loadingSubject.next(false);
        },
        error: (error) => {
          console.error('Error:', error);
          this.loadingSubject.next(false);
        }
      });
  }
}

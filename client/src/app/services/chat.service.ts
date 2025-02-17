import { Injectable } from '@angular/core';
import { Message } from '../interfaces/message';
import { BehaviorSubject, Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messageSubject = new Subject<Message>();
  private loadingSubject = new BehaviorSubject<boolean>(false);

  messages$ = this.messageSubject.asObservable();
  loading$ = this.loadingSubject.asObservable();

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  sendMessage(message: Message) {
    // Emitir mensaje del usuario
    this.messageSubject.next(message);

    // Activar loading
    this.loadingSubject.next(true);

    // Enviar mensaje al servidor
    this.http.post<{messages: Message[]}>(`${this.apiUrl}/chat`, {
      content: message.content,
      type: 'Human'
    }).subscribe({
      next: (response) => {
        // Emitir respuestas del bot
        response.messages.forEach(msg => {
          this.messageSubject.next(msg);
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

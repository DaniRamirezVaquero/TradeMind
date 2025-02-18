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
  private sessionId: string | null = null;

  messages$ = this.messageSubject.asObservable();
  loading$ = this.loadingSubject.asObservable();

  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  sendMessage(message: Message) {
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
          // Guardar el sessionId de la respuesta
          this.sessionId = response.sessionId;

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

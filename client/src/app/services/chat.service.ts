import { Injectable } from '@angular/core';
import { Message } from '../interfaces/message';
import { Subject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private messageSubject = new Subject<Message>();
  messages$ = this.messageSubject.asObservable();
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  sendMessage(message: Message) {
    // Emitir mensaje del usuario
    this.messageSubject.next(message);

    // Enviar mensaje al servidor
    this.http.post<{messages: Message[]}>(`${this.apiUrl}/chat`, {
      content: message.content,
      type: 'Human'
    }).subscribe(response => {
      // Emitir respuestas del bot
      response.messages.forEach(msg => {
        this.messageSubject.next(msg);
      });
    });
  }
}

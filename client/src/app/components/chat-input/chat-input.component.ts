import { Component } from '@angular/core';
import { TextareaModule } from 'primeng/textarea';
import { ButtonModule } from 'primeng/button';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { Message } from '../../interfaces/message';

@Component({
  selector: 'app-chat-input',
  imports: [
    TextareaModule,
    ButtonModule,
    FormsModule
  ],
  templateUrl: './chat-input.component.html',
  styleUrl: './chat-input.component.css'
})
export class ChatInputComponent {
  message: string = '';

  constructor(private chatService: ChatService) {}

  sendMessage() {
    if (this.message.trim()) {
      const newMessage: Message = {
        content: this.message,
        id: Date.now().toString(),
        type: 'Human',
      };

      this.chatService.sendMessage(newMessage);
      this.message = '';
    }
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}

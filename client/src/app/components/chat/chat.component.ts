import { Component } from '@angular/core';
import { InputTextModule } from 'primeng/inputtext';
import { MessageModule } from 'primeng/message';
import { ButtonModule } from 'primeng/button';
import { RippleModule } from 'primeng/ripple';
import { FormsModule } from '@angular/forms';
import { ChatInputComponent } from '../chat-input/chat-input.component';
import { ChatWindowComponent } from '../chat-window/chat-window.component';

@Component({
  selector: 'app-chat',
  imports: [
    InputTextModule,
    ButtonModule,
    MessageModule,
    FormsModule,
    ChatInputComponent,
    ChatWindowComponent
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css'
})
export class ChatComponent {
  messages: {id: number, severity: string, summary: string, detail: string }[] = [];
  userMessage: string = '';

  constructor() {}

  sendMessage() {
    if (this.userMessage.trim().length > 0) {
      this.messages.push({id: (this.messages.length + 1), severity: 'info', summary: 'User', detail: this.userMessage });
      this.userMessage = '';
    }
  }
}

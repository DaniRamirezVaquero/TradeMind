import { Component, OnDestroy, OnInit } from '@angular/core';
import { TextareaModule } from 'primeng/textarea';
import { ButtonModule } from 'primeng/button';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../services/chat.service';
import { Message } from '../../interfaces/message';
import { Subscription } from 'rxjs';

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
export class ChatInputComponent implements OnInit, OnDestroy {
  message: string = '';
  isLoading: boolean = false;

  subscriptions: Subscription[] = [];

  constructor(private chatService: ChatService) {}

  ngOnDestroy(): void {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
  }

  ngOnInit(): void {
    const loadingSubscription = this.chatService.loading$.subscribe(
      loading => this.isLoading = loading
    );

    this.subscriptions.push(loadingSubscription);
  }

  sendMessage() {
    if (this.message.trim() && !this.isLoading) {
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

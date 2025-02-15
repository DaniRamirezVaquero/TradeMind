import { Component } from '@angular/core';
import { TextareaModule } from 'primeng/textarea';

@Component({
  selector: 'app-chat-input',
  imports: [
    TextareaModule
  ],
  templateUrl: './chat-input.component.html',
  styleUrl: './chat-input.component.css'
})
export class ChatInputComponent {
  autoResize(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }
}

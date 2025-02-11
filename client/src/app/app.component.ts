import { Component } from '@angular/core';
import { ChatComponent } from './components/chat/chat.component';

@Component({
  selector: 'app-root',
  imports: [
    ChatComponent
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'client';
}

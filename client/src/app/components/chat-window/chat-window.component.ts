import { AfterViewChecked, Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ScrollPanel, ScrollPanelModule } from 'primeng/scrollpanel';
import { MessageModule } from 'primeng/message';
import { PanelModule } from 'primeng/panel';
import { Message } from '../../interfaces/message';
import { Subscription } from 'rxjs';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-chat-window',
  imports: [
    ScrollPanelModule,
    MessageModule,
    PanelModule
  ],
  templateUrl: './chat-window.component.html',
  styleUrl: './chat-window.component.css'
})


export class ChatWindowComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('scrollPanel') private scrollPanel!: ScrollPanel;
  messages: Message[] = [];

  private subscription!: Subscription;

  constructor(private chatService: ChatService) {}

  ngOnInit() {
    this.subscription = this.chatService.messages$.subscribe(message => {
      this.messages.push(message);
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  private scrollToBottom() {
    if (this.scrollPanel && this.scrollPanel.contentViewChild) {
      this.scrollPanel.refresh();
      const element = this.scrollPanel.contentViewChild.nativeElement;
      element.scrollTo({
        top: element.scrollHeight,
        behavior: 'smooth'
      });
    }
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}

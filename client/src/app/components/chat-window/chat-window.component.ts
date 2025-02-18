import { AfterViewChecked, Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { ScrollPanel, ScrollPanelModule } from 'primeng/scrollpanel';
import { MessageModule } from 'primeng/message';
import { PanelModule } from 'primeng/panel';
import { Message } from '../../interfaces/message';
import { Subscription } from 'rxjs';
import { ChatService } from '../../services/chat.service';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { MarkdownModule } from 'ngx-markdown';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-chat-window',
  imports: [
    ScrollPanelModule,
    MessageModule,
    PanelModule,
    ProgressSpinnerModule,
    MarkdownModule,
    ButtonModule
  ],
  templateUrl: './chat-window.component.html',
  styleUrl: './chat-window.component.css'
})

export class ChatWindowComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('scrollPanel') private scrollPanel!: ScrollPanel;
  messages: Message[] = [{
    id: "0",
    type: 'AI',
    content: 'Hola! Soy TradeMind, tu agente especializado en reventa de smartphones, en que te puedo ayudar?'
  }];
  isLoading: boolean = false;

  private subscriptions: Subscription[] = [];

  constructor(private chatService: ChatService) {}

  ngOnInit() {
    const messagesSubscription = this.chatService.messages$.subscribe(message => {
      if (message.content !== '') {
        this.messages.push(message);
      }
    });

    const loadingSubscription = this.chatService.loading$.subscribe(loading => {
      this.isLoading = loading;
    });

    this.subscriptions.push(messagesSubscription, loadingSubscription);
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

  onCopyToClipboard() {
    console.log('Copied to clipboard!');
  }

  ngOnDestroy() {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
  }
}

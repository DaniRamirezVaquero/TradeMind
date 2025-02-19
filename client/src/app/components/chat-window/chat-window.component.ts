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
  messages: Message[] = [];
  isLoading: boolean = false;
  private shouldScroll: boolean = true;

  private subscriptions: Subscription[] = [];

  constructor(private chatService: ChatService) {}

  async ngOnInit() {
    // Establecer loading mientras inicializamos
    this.isLoading = true;

    try {
      // Inicializar la sesión
      const initialMessages = await this.chatService.initializeSession();

      // Añadir los mensajes iniciales directamente al array
      if (initialMessages && initialMessages.length > 0) {
        this.messages = initialMessages;
        this.shouldScroll = true;
      }
    } catch (error) {
      console.error('Error initializing chat:', error);
    } finally {
      this.isLoading = false;
    }

    // Suscribirse a nuevos mensajes
    const messagesSubscription = this.chatService.messages$.subscribe(message => {
      if (message.content !== '') {
        // Verificar si el mensaje ya existe para evitar duplicados
        const messageExists = this.messages.some(
          m => m.content === message.content && m.type === message.type
        );

        if (!messageExists) {
          this.messages.push(message);
          // Activar el scroll cuando se añade un nuevo mensaje
          this.shouldScroll = true;
        }
      }
    });

    const loadingSubscription = this.chatService.loading$.subscribe(loading => {
      this.isLoading = loading;
      // Si se completa la carga, activar el scroll
      if (!loading) {
        this.shouldScroll = true;
      }
    });

    this.subscriptions.push(messagesSubscription, loadingSubscription);
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  private scrollToBottom() {
    if (this.scrollPanel && this.scrollPanel.contentViewChild) {
      // Asegurarse de que el panel esté actualizado
      this.scrollPanel.refresh();

      // Usar setTimeout para asegurar que el scroll se ejecute después de que el DOM se actualice
      setTimeout(() => {
        const element = this.scrollPanel?.contentViewChild?.nativeElement;
        element.scrollTo({
          top: element.scrollHeight,
          behavior: 'smooth'
        });
      }, 0);
    }
  }

  onCopyToClipboard() {
    console.log('Copied to clipboard!');
  }

  ngOnDestroy() {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
  }
}

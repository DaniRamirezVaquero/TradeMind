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
import { ChartModule } from 'primeng/chart';

@Component({
  selector: 'app-chat-window',
  imports: [
    ScrollPanelModule,
    MessageModule,
    PanelModule,
    ProgressSpinnerModule,
    MarkdownModule,
    ButtonModule,
    ChartModule
  ],
  templateUrl: './chat-window.component.html',
  styleUrl: './chat-window.component.css'
})

export class ChatWindowComponent implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('scrollPanel') private scrollPanel!: ScrollPanel;
  messages: Message[] = [];
  isLoading: boolean = false;
  private shouldScroll: boolean = true;
  chartOptions: any;
  messageGroups: MessageGroup[] = [];

  private subscriptions: Subscription[] = [];

  constructor(private chatService: ChatService) {
    this.initChartOptions();
  }

  private initChartOptions() {
    this.chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: '#ffffff'
          }
        },
        title: {
          display: true,
          text: 'Evolución del Precio',
          color: '#ffffff'
        }
      },
      scales: {
        x: {
          ticks: {
            color: '#ffffff'
          },
          grid: {
            color: 'rgba(255,255,255,0.2)'
          }
        },
        y: {
          ticks: {
            color: '#ffffff',
            callback: (value: number) => `${value}€`
          },
          grid: {
            color: 'rgba(255,255,255,0.2)'
          }
        }
      }
    };
  }

  async ngOnInit() {
    // Establecer loading mientras inicializamos
    this.isLoading = true;

    try {
      // Inicializar la sesión
      const initialMessages = await this.chatService.initializeSession();

      // Procesar los mensajes iniciales
      if (initialMessages && initialMessages.length > 0) {
        this.messageGroups = this.groupMessages(initialMessages);
        // Process tool results for charts
        initialMessages.forEach(message => {
          if (message.type === 'tool_result' && message.content) {
            try {
              const group = this.messageGroups.find(g => g.toolResult === message);
              if (group) {
                group.chartData = this.createChartData(message.content);
              }
            } catch (e) {
              console.error('Error parsing initial tool result:', e);
            }
          }
        });

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
        // Add message to appropriate group
        if (message.type === 'Human') {
          this.messageGroups.push({ humanMessage: message });
        } else if (message.type === 'AI') {
          const lastGroup = this.messageGroups[this.messageGroups.length - 1];
          if (lastGroup) {
            lastGroup.aiMessage = message;
          }
        }
        this.shouldScroll = true;
      }
    });

    const loadingSubscription = this.chatService.loading$.subscribe(loading => {
      this.isLoading = loading;
      // Si se completa la carga, activar el scroll
      if (!loading) {
        this.shouldScroll = true;
      }
    });

    const toolResultSubscription = this.chatService.toolResults$.subscribe(message => {
      if (message.type === 'tool_result' && message.content) {
        console.log('Received tool result:', message);
        const lastGroup = this.messageGroups[this.messageGroups.length - 1];
        if (lastGroup) {
          lastGroup.toolResult = message;
          lastGroup.chartData = this.createChartData(message.content);
          this.shouldScroll = true;
        }
      }
    });

    this.subscriptions.push(messagesSubscription, loadingSubscription, toolResultSubscription);
  }

  private isPriceData(data: any): boolean {
    // Verificar si tenemos la estructura correcta con graph_data
    if (!data || !data.graph_data) {
      console.log('Missing data or graph_data property');
      return false;
    }

    // Verificar el formato de los datos dentro de graph_data
    return Object.entries(data.graph_data).every(([key, value]) => {
      // Convertir fecha de DD-MM-YYYY a YYYY-MM-DD para Date.parse
      const [day, month, year] = key.split('-');
      const isoDate = `${year}-${month}-${day}`;
      const dateValid = !isNaN(Date.parse(isoDate));
      const valueValid = typeof value === 'number';

      console.log('Validating entry:', {
        originalDate: key,
        isoDate,
        dateValid,
        valueValid,
        value
      });

      return dateValid && valueValid;
    });
  }

  private createChartData(jsonString: string): any {
    try {
      console.log('Received jsonString:', jsonString);
      const toolResult = JSON.parse(jsonString);
      console.log('Parsed toolResult:', toolResult);

      if (!this.isPriceData(toolResult)) {
        console.log('Invalid data format or not a graph data');
        return null;
      }

      const priceData = toolResult.graph_data;

      // Convertir fechas a formato Date para ordenar correctamente
      const sortedDates = Object.keys(priceData).sort((a, b) => {
        const [dayA, monthA, yearA] = a.split('-');
        const [dayB, monthB, yearB] = b.split('-');
        return new Date(`${yearA}-${monthA}-${dayA}`).getTime() -
               new Date(`${yearB}-${monthB}-${dayB}`).getTime();
      });

      return {
        labels: sortedDates.map(date => {
          const [day, month, year] = date.split('-');
          return `${day}/${month}/${year.slice(-2)}`; // Formato DD/MM/YY
        }),
        datasets: [{
          label: 'Precio Estimado (€)',
          data: sortedDates.map(date => priceData[date]),
          fill: false,
          borderColor: '#8c62ff',
          tension: 0.4,
          pointBackgroundColor: '#713dff'
        }]
      };

    } catch (error) {
      console.error('Error creating chart data:', error);
      console.error('Problematic input:', jsonString);
      return null;
    }
  }

  private groupMessages(messages: Message[]) {
    const groups: MessageGroup[] = [];
    let currentGroup: MessageGroup = {};

    messages.forEach(message => {
      if (message.type === 'Human') {
        if (Object.keys(currentGroup).length > 0) {
          groups.push(currentGroup);
        }
        currentGroup = { humanMessage: message };
      } else if (message.type === 'AI') {
        currentGroup.aiMessage = message;
      } else if (message.type === 'tool_result') {
        currentGroup.toolResult = message;
      }
    });

    // Add the last group if it exists
    if (Object.keys(currentGroup).length > 0) {
      groups.push(currentGroup);
    }

    return groups;
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

  ngOnDestroy() {
    this.subscriptions.forEach(subscription => subscription.unsubscribe());
  }
}

export interface MessageGroup {
  aiMessage?: Message;
  toolResult?: Message;
  humanMessage?: Message;
  chartData?: any;  // Añadir chartData al grupo
}

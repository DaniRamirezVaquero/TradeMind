import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { providePrimeNG } from 'primeng/config';
import { MyPreset } from './mytheme';


import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    providePrimeNG({
      theme: {
          preset: MyPreset,
          options: {
            darkModeSelector: '.dark-mode',
            cssLayer: {
              name: 'primeng',
              order: 'tailwind, primeng'
            }
          }
      }
  })
  ]
};

import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.ezeegenie.app',
  appName: 'EzeeGenie',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
  }
};

export default config;

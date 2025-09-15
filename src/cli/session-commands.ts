import { SimpleSessionManager } from '../session/SimpleSessionManager';

export function addSessionCommands(program: any) {
  const session = program.command('session');

  session
    .command('save <name>')
    .description('Save current session')
    .action((name: string) => {
      const manager = new SimpleSessionManager();
      const sessionData = {
        timestamp: new Date().toISOString(),
        name: name,
        cwd: process.cwd(),
        environment: {
          node_version: process.version,
          platform: process.platform,
        }
      };
      manager.saveSession(name, sessionData);
    });

  session
    .command('list')
    .description('List saved sessions')
    .action(() => {
      const manager = new SimpleSessionManager();
      const sessions = manager.listSessions();
      console.log('\nSaved Sessions:');
      if (sessions.length === 0) {
        console.log('  No sessions found');
      } else {
        sessions.forEach(s => console.log(`  - ${s}`));
      }
    });

  session
    .command('load <filename>')
    .description('Load and display session data')
    .action((filename: string) => {
      const manager = new SimpleSessionManager();
      try {
        const data = manager.loadSession(filename);
        console.log('\nSession Data:');
        console.log(JSON.stringify(data, null, 2));
      } catch (error) {
        console.error(`Error loading session: ${error instanceof Error ? error.message : String(error)}`);
      }
    });
}
import Map from './components/Map';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import TelegramLoginButton from './components/TelegramLoginButton';
import axios from 'axios';
import { useState } from 'react';
import Leaderboard from './components/Leaderboard';
import { AppBar, Toolbar, Button } from '@mui/material';
import UserProfile from './components/UserProfile';
import { Box, Typography } from '@mui/material';
import Tournaments from './components/Tournaments';
import Challenges from './components/Challenges';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1976d2' },
    secondary: { main: '#f50057' },
    background: { default: '#f4f6fa' },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});

function App() {
  const [user, setUser] = useState<any>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [page, setPage] = useState<'map' | 'leaderboard' | 'profile' | 'tournaments' | 'challenges'>('map');

  const handleTelegramAuth = async (tgUser: any) => {
    try {
      console.log('Telegram auth data:', tgUser);
      const response = await axios.post('http://localhost:8000/api/auth/telegram', tgUser);
      localStorage.setItem('access_token', response.data.access_token);
      setToken(response.data.access_token);
      setUser(tgUser);
      console.log('Auth successful:', response.data);
    } catch (error) {
      console.error('Auth error:', error);
      alert('Ошибка авторизации через Telegram');
    }
  };

  if (!token) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center', 
          minHeight: '100vh',
          gap: 2
        }}>
          <Typography variant="h4" gutterBottom>
            Street Pong Bot
          </Typography>
          <Typography variant="body1" color="text.secondary" gutterBottom>
            Войдите через Telegram для доступа к приложению
          </Typography>
          <TelegramLoginButton botName="Street_pong_test_bot" onAuth={handleTelegramAuth} />
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar>
          <Button color={page === 'map' ? 'primary' : 'inherit'} onClick={() => setPage('map')}>Карта</Button>
          <Button color={page === 'leaderboard' ? 'primary' : 'inherit'} onClick={() => setPage('leaderboard')}>Рейтинг</Button>
          <Button color={page === 'profile' ? 'primary' : 'inherit'} onClick={() => setPage('profile')}>Профиль</Button>
          <Button color={page === 'tournaments' ? 'primary' : 'inherit'} onClick={() => setPage('tournaments')}>Турниры</Button>
          <Button color={page === 'challenges' ? 'primary' : 'inherit'} onClick={() => setPage('challenges')}>Вызовы</Button>
        </Toolbar>
      </AppBar>
      {page === 'map' ? <Map /> : 
       page === 'leaderboard' ? <Leaderboard /> : 
       page === 'profile' ? <UserProfile /> : 
       page === 'tournaments' ? <Tournaments /> :
       <Challenges />}
    </ThemeProvider>
  );
}

export default App;

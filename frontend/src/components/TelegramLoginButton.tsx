import { useEffect } from 'react';
import { Button, Box, Typography } from '@mui/material';

interface TelegramLoginButtonProps {
  botName: string;
  onAuth: (user: any) => void;
}

const TelegramLoginButton = ({ botName, onAuth }: TelegramLoginButtonProps) => {
  useEffect(() => {
    // @ts-ignore
    window.onTelegramAuth = (user: any) => {
      onAuth(user);
    };
    // eslint-disable-next-line
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?7';
    script.async = true;
    script.setAttribute('data-telegram-login', botName);
    script.setAttribute('data-size', 'large');
    script.setAttribute('data-userpic', 'true');
    script.setAttribute('data-request-access', 'write');
    script.setAttribute('data-userpic', 'true');
    script.setAttribute('data-onauth', 'onTelegramAuth(user)');
    document.getElementById('telegram-login-btn-root')?.appendChild(script);
    return () => {
      document.getElementById('telegram-login-btn-root')?.removeChild(script);
    };
  }, [botName, onAuth]);

  const handleTestAuth = () => {
    // Тестовые данные для проверки backend
    const testUser = {
      id: 123456789,
      first_name: "Test",
      username: "testuser",
      photo_url: "https://t.me/i/userpic/320/testuser.jpg",
      auth_date: Math.floor(Date.now() / 1000),
      hash: "test_hash_for_development"
    };
    onAuth(testUser);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <div id="telegram-login-btn-root" style={{ display: 'flex', justifyContent: 'center', margin: 24 }} />
      
      {/* Временная кнопка для тестирования */}
      <Box sx={{ mt: 2, p: 2, border: '1px dashed #ccc', borderRadius: 2 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Если кнопка Telegram не работает, используйте тестовую авторизацию:
        </Typography>
        <Button 
          variant="outlined" 
          onClick={handleTestAuth}
          sx={{ mt: 1 }}
        >
          Тестовая авторизация
        </Button>
      </Box>
    </Box>
  );
};

export default TelegramLoginButton; 
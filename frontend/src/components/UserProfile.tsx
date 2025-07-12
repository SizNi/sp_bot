import { useEffect, useState } from 'react';
import axios from 'axios';
import { Paper, Typography, Box, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Avatar, Chip } from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';

interface MatchHistory {
  date: string;
  opponent_id: number;
  score: string;
  rating_before: number;
  rating_after: number;
  change: number;
  is_win: boolean;
}

const UserProfile = () => {
  const [history, setHistory] = useState<MatchHistory[]>([]);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Получаем данные пользователя из токена или localStorage
    const token = localStorage.getItem('access_token');
    if (token) {
      // В реальном приложении здесь нужно декодировать JWT и получить user_id
      // Пока используем фиксированный ID для демонстрации
      const userId = 1; // Замените на реальный ID пользователя
      axios.get(`http://localhost:8000/api/user/${userId}/history`).then(res => setHistory(res.data));
    }
  }, []);

  return (
    <Box sx={{ maxWidth: 800, margin: '32px auto', padding: '0 16px' }}>
      <Typography variant="h4" align="center" gutterBottom>Мой профиль</Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>История матчей</Typography>
        {history.length === 0 ? (
          <Typography color="text.secondary">История матчей пуста</Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Дата</TableCell>
                  <TableCell>Соперник</TableCell>
                  <TableCell>Счёт</TableCell>
                  <TableCell>Рейтинг до</TableCell>
                  <TableCell>Рейтинг после</TableCell>
                  <TableCell>Изменение</TableCell>
                  <TableCell>Результат</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {history.map((match, index) => (
                  <TableRow key={index}>
                    <TableCell>{new Date(match.date).toLocaleDateString()}</TableCell>
                    <TableCell>Пользователь {match.opponent_id}</TableCell>
                    <TableCell>{match.score}</TableCell>
                    <TableCell>{match.rating_before}</TableCell>
                    <TableCell>{match.rating_after}</TableCell>
                    <TableCell>
                      <Chip 
                        label={`${match.change > 0 ? '+' : ''}${match.change}`}
                        color={match.change > 0 ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {match.is_win ? (
                        <CheckCircle color="success" />
                      ) : (
                        <Cancel color="error" />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
};

export default UserProfile; 
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Avatar, Typography, Box } from '@mui/material';

interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  rating: number;
  place: number;
}

const Leaderboard = () => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/leaderboard').then(res => setUsers(res.data));
  }, []);

  return (
    <Box sx={{ maxWidth: 600, margin: '32px auto' }}>
      <Typography variant="h4" align="center" gutterBottom>Рейтинговая таблица</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Место</TableCell>
              <TableCell>Пользователь</TableCell>
              <TableCell>Рейтинг</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map(user => (
              <TableRow key={user.id}>
                <TableCell>{user.place}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Avatar src={user.avatar_url} alt={user.username} />
                    <span>{user.username || user.first_name}</span>
                  </Box>
                </TableCell>
                <TableCell>{user.rating}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default Leaderboard; 
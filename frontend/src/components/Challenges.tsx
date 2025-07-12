import { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  Paper, Typography, Box, Button, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField, Chip
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

interface Challenge {
  id: number;
  challenger_username: string;
  challenged_username: string;
  status: string;
  created_at: string;
  is_challenger: boolean;
}

const Challenges = () => {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [newChallenge, setNewChallenge] = useState({
    challenged_username: ''
  });

  useEffect(() => {
    loadChallenges();
  }, []);

  const loadChallenges = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/challenges');
      setChallenges(response.data);
    } catch (error) {
      console.error('Error loading challenges:', error);
    }
  };

  const handleCreateChallenge = async () => {
    try {
      await axios.post('http://localhost:8000/api/challenges', {
        challenged_username: newChallenge.challenged_username
      });
      setOpenCreateDialog(false);
      setNewChallenge({ challenged_username: '' });
      loadChallenges();
      alert('Вызов создан! Проверьте Telegram для подтверждения.');
    } catch (error: any) {
      console.error('Error creating challenge:', error);
      alert(error.response?.data?.detail || 'Ошибка создания вызова');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'accepted': return 'success';
      case 'declined': return 'error';
      case 'completed': return 'default';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending': return 'Ожидает ответа';
      case 'accepted': return 'Принят';
      case 'declined': return 'Отклонен';
      case 'completed': return 'Завершен';
      default: return status;
    }
  };

  return (
    <Box sx={{ maxWidth: 800, margin: '32px auto', padding: '0 16px' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Вызовы</Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => setOpenCreateDialog(true)}
        >
          Создать вызов
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Вызов</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Дата</TableCell>
              <TableCell>Ваша роль</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {challenges.map(challenge => (
              <TableRow key={challenge.id}>
                <TableCell>
                  <Typography variant="body2">
                    <strong>@{challenge.challenger_username}</strong> vs <strong>@{challenge.challenged_username}</strong>
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={getStatusText(challenge.status)}
                    color={getStatusColor(challenge.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(challenge.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  {challenge.is_challenger ? 'Вызывающий' : 'Вызванный'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Диалог создания вызова */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Создать вызов</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Введите username игрока, которого хотите вызвать (без @):
          </Typography>
          <TextField
            fullWidth
            label="Username игрока"
            value={newChallenge.challenged_username}
            onChange={(e) => setNewChallenge({...newChallenge, challenged_username: e.target.value})}
            margin="normal"
            placeholder="username"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Отмена</Button>
          <Button onClick={handleCreateChallenge} variant="contained">
            Создать вызов
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Challenges; 
import { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  Paper, Typography, Box, Button, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField, FormControl, InputLabel, 
  Select, MenuItem, Chip
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

interface Tournament {
  id: number;
  title: string;
  spot_id: number;
  datetime: string;
  description?: string;
  status: string;
  created_at: string;
  participants_count: number;
}

interface Location {
  id: number;
  name: string;
}

const Tournaments = () => {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [newTournament, setNewTournament] = useState({
    title: '',
    spot_id: '',
    datetime: '',
    description: ''
  });

  useEffect(() => {
    loadTournaments();
    loadLocations();
  }, []);

  const loadTournaments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/tournaments');
      setTournaments(response.data);
    } catch (error) {
      console.error('Error loading tournaments:', error);
    }
  };

  const loadLocations = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/locations');
      setLocations(response.data);
    } catch (error) {
      console.error('Error loading locations:', error);
    }
  };

  const handleCreateTournament = async () => {
    try {
      await axios.post('http://localhost:8000/api/tournaments', {
        title: newTournament.title,
        spot_id: parseInt(newTournament.spot_id),
        datetime: newTournament.datetime,
        description: newTournament.description || null
      });
      setOpenCreateDialog(false);
      setNewTournament({ title: '', spot_id: '', datetime: '', description: '' });
      loadTournaments();
    } catch (error) {
      console.error('Error creating tournament:', error);
      alert('Ошибка создания турнира');
    }
  };

  const handleJoinTournament = async (tournamentId: number) => {
    try {
      await axios.post(`http://localhost:8000/api/tournaments/${tournamentId}/join`);
      alert('Успешно зарегистрировались на турнир!');
      loadTournaments();
    } catch (error) {
      console.error('Error joining tournament:', error);
      alert('Ошибка регистрации на турнир');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'success';
      case 'started': return 'warning';
      case 'completed': return 'default';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'open': return 'Открыт для регистрации';
      case 'started': return 'Идет турнир';
      case 'completed': return 'Завершен';
      default: return status;
    }
  };

  return (
    <Box sx={{ maxWidth: 1000, margin: '32px auto', padding: '0 16px' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Турниры</Typography>
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={() => setOpenCreateDialog(true)}
        >
          Создать турнир
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Название</TableCell>
              <TableCell>Место проведения</TableCell>
              <TableCell>Дата и время</TableCell>
              <TableCell>Участники</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tournaments.map(tournament => (
              <TableRow key={tournament.id}>
                <TableCell>{tournament.title}</TableCell>
                <TableCell>
                  {locations.find(l => l.id === tournament.spot_id)?.name || `Спот ${tournament.spot_id}`}
                </TableCell>
                <TableCell>
                  {new Date(tournament.datetime).toLocaleString()}
                </TableCell>
                <TableCell>{tournament.participants_count}</TableCell>
                <TableCell>
                  <Chip 
                    label={getStatusText(tournament.status)}
                    color={getStatusColor(tournament.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {tournament.status === 'open' && (
                    <Button 
                      variant="outlined" 
                      size="small"
                      onClick={() => handleJoinTournament(tournament.id)}
                    >
                      Присоединиться
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Диалог создания турнира */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Создать турнир</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Название турнира"
            value={newTournament.title}
            onChange={(e) => setNewTournament({...newTournament, title: e.target.value})}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Место проведения</InputLabel>
            <Select
              value={newTournament.spot_id}
              onChange={(e) => setNewTournament({...newTournament, spot_id: e.target.value})}
            >
              {locations.map(location => (
                <MenuItem key={location.id} value={location.id}>
                  {location.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Дата и время"
            type="datetime-local"
            value={newTournament.datetime}
            onChange={(e) => setNewTournament({...newTournament, datetime: e.target.value})}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            fullWidth
            label="Описание (необязательно)"
            value={newTournament.description}
            onChange={(e) => setNewTournament({...newTournament, description: e.target.value})}
            margin="normal"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Отмена</Button>
          <Button onClick={handleCreateTournament} variant="contained">
            Создать
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Tournaments; 
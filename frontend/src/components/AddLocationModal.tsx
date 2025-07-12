import { Modal, Box, Typography, TextField, Button, MenuItem, Checkbox, FormControlLabel } from '@mui/material';
import { useState } from 'react';
import axios from 'axios';

interface AddLocationModalProps {
  open: boolean;
  onClose: () => void;
  lat?: number;
  lng?: number;
  onLocationAdded: (location: any) => void;
  netTypes: string[];
}

export default function AddLocationModal({ open, onClose, lat, lng, onLocationAdded, netTypes }: AddLocationModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [tablesCount, setTablesCount] = useState(1);
  const [netType, setNetType] = useState('');
  const [hasRoof, setHasRoof] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [photos, setPhotos] = useState<File[]>([]);

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPhotos(Array.from(e.target.files));
    }
  };

  const handleTablesCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (!value || value < 1) {
      setTablesCount(1);
    } else {
      setTablesCount(Math.floor(value));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lat || !lng) return;
    setIsSubmitting(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('name', name);
      formData.append('description', description);
      formData.append('latitude', String(lat));
      formData.append('longitude', String(lng));
      formData.append('tables_count', String(tablesCount));
      formData.append('net_type', netType);
      formData.append('has_roof', String(hasRoof));
      photos.forEach((file) => formData.append('photos', file));

      const response = await axios.post('http://localhost:8000/api/locations', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      onLocationAdded(response.data);
      setName('');
      setDescription('');
      setTablesCount(1);
      setNetType('');
      setHasRoof(false);
      setPhotos([]);
    } catch (err: any) {
      setError('Ошибка при добавлении точки');
    } finally {
      setIsSubmitting(false);
      onClose();
    }
  };

  return (
    <Modal open={open} onClose={onClose} aria-labelledby="add-location-modal-title">
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 400,
        bgcolor: 'background.paper',
        boxShadow: 24,
        p: 4,
        borderRadius: 2,
      }}>
        <Typography variant="h6" id="add-location-modal-title" gutterBottom>
          Добавить новую точку
        </Typography>
        <form onSubmit={handleSubmit} encType="multipart/form-data">
          <TextField
            label="Название"
            value={name}
            onChange={e => setName(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          />
          <TextField
            label="Описание"
            value={description}
            onChange={e => setDescription(e.target.value)}
            fullWidth
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
          <TextField
            label="Количество столов"
            type="number"
            value={tablesCount}
            onChange={handleTablesCountChange}
            fullWidth
            inputProps={{ min: 1 }}
            sx={{ mb: 2 }}
          />
          <TextField
            label="Тип сетки"
            select
            value={netType}
            onChange={e => setNetType(e.target.value)}
            fullWidth
            required
            sx={{ mb: 2 }}
          >
            {netTypes.map(type => (
              <MenuItem key={type} value={type}>{type}</MenuItem>
            ))}
          </TextField>
          <FormControlLabel
            control={<Checkbox checked={hasRoof} onChange={e => setHasRoof(e.target.checked)} />}
            label="Есть крыша"
            sx={{ mb: 2 }}
          />
          <Button
            variant="outlined"
            component="label"
            fullWidth
            sx={{ mb: 2 }}
          >
            {photos.length > 0 ? `Выбрано файлов: ${photos.length}` : 'Прикрепить фотографии'}
            <input
              type="file"
              accept="image/*"
              multiple
              hidden
              onChange={handlePhotoChange}
            />
          </Button>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button onClick={onClose} disabled={isSubmitting}>Отмена</Button>
            <Button type="submit" variant="contained" disabled={isSubmitting}>
              {isSubmitting ? 'Добавление...' : 'Добавить'}
            </Button>
          </Box>
          {error && <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>}
        </form>
      </Box>
    </Modal>
  );
} 
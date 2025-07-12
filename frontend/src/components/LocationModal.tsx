import { Modal, Box, Typography, Button, IconButton, Rating as MuiRating, TextField } from '@mui/material';
import { Close as CloseIcon, ContentCopy as ContentCopyIcon, Star as StarIcon } from '@mui/icons-material';
import RoomIcon from '@mui/icons-material/Room';
import SportsTennisIcon from '@mui/icons-material/SportsTennis';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

interface Location {
  id: number;
  name: string;
  description: string;
  latitude: number;
  longitude: number;
  tables_count: number;
  net_type: string;
  has_roof: boolean;
  author: {
    username: string;
    first_name: string;
    last_name: string;
  };
  photos: Array<{
    id: number;
    file_path: string;
    url: string;
  }>;
  average_rating: number;
  ratings_count: number;
}

interface Rating {
  id: number;
  score: number;
  comment: string | null;
  created_at: string;
  user: {
    username: string;
  };
}

interface LocationModalProps {
  location: Location | null;
  open: boolean;
  onClose: () => void;
}

export default function LocationModal({ location, open, onClose }: LocationModalProps) {
  const [copied, setCopied] = useState(false);
  const [userRating, setUserRating] = useState<number | null>(null);
  const [comment, setComment] = useState('');
  const [ratings, setRatings] = useState<Rating[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (location) {
      // Загружаем рейтинги при открытии модального окна
      fetchRatings();
    }
  }, [location]);

  const fetchRatings = async () => {
    if (!location) return;
    try {
      const response = await axios.get(`http://localhost:8000/api/locations/${location.id}/ratings`);
      setRatings(response.data);
    } catch (error) {
      console.error('Error fetching ratings:', error);
    }
  };

  const handleCopyCoordinates = () => {
    if (location) {
      navigator.clipboard.writeText(`${location.latitude}, ${location.longitude}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRatingSubmit = async () => {
    if (!location || !userRating) return;
    
    setIsSubmitting(true);
    try {
      await axios.post(`http://localhost:8000/api/locations/${location.id}/ratings`, {
        score: userRating,
        comment: comment || null
      });
      await fetchRatings();
      setComment('');
    } catch (error) {
      console.error('Error submitting rating:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!location) return null;

  // Настройки для слайдера
  const sliderSettings = {
    dots: true,
    infinite: location.photos.length > 1,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    arrows: true,
  };

  if (location && location.photos && location.photos.length > 0) {
    // Для отладки: вывести url всех фото
    // eslint-disable-next-line no-console
    console.log('Фото для слайдера:', location.photos.map(p => p.url));
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="location-modal-title"
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 400,
        maxHeight: '90vh',
        overflowY: 'auto',
        bgcolor: 'background.paper',
        boxShadow: 24,
        p: 4,
        borderRadius: 2,
      }}>
        <IconButton
          sx={{ position: 'absolute', right: 8, top: 8 }}
          onClick={onClose}
        >
          <CloseIcon />
        </IconButton>

        <Typography variant="h5" component="h2" gutterBottom>
          {location.name}
        </Typography>

        {/* Слайдер с фотографиями */}
        {location.photos && location.photos.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Slider {...sliderSettings}>
              {location.photos.map((photo) => (
                <div key={photo.id}>
                  <img
                    src={`http://localhost:8000${photo.url}`}
                    alt={`Фото ${location.name}`}
                    style={{ width: '100%', maxHeight: 300, objectFit: 'cover', borderRadius: 8 }}
                  />
                </div>
              ))}
            </Slider>
          </Box>
        )}

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1" color="text.secondary">
            Координаты:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography>
              {location.latitude}, {location.longitude}
            </Typography>
            <IconButton onClick={handleCopyCoordinates} size="small">
              <ContentCopyIcon />
            </IconButton>
            <IconButton
              component="a"
              href={`https://yandex.ru/maps/?ll=${location.longitude}%2C${location.latitude}&z=17&pt=${location.longitude},${location.latitude},pm2rdm`}
              target="_blank"
              rel="noopener noreferrer"
              size="small"
              title="Открыть в Яндекс.Картах"
            >
              <RoomIcon sx={{ color: '#fc3f1d' }} />
            </IconButton>
            <IconButton
              component="a"
              href={`https://2gis.ru/?query=${location.latitude},${location.longitude}`}
              target="_blank"
              rel="noopener noreferrer"
              size="small"
              title="Открыть в 2ГИС"
            >
              <RoomIcon sx={{ color: '#00b341' }} />
            </IconButton>
            {copied && (
              <Typography variant="caption" color="success.main">
                Скопировано!
              </Typography>
            )}
          </Box>
        </Box>

        <Typography variant="body1" paragraph>
          {location.description}
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
          {location.tables_count > 0 && (
            <Box>
              <Typography variant="subtitle2">
                Количество столов: {location.tables_count}
              </Typography>
            </Box>
          )}
          {location.net_type && (
            <Box>
              <Typography variant="subtitle2">
                Тип сетки: {location.net_type}
              </Typography>
            </Box>
          )}
          <Box>
            <Typography variant="subtitle2">
              Крыша: {location.has_roof ? 'Есть' : 'Нет'}
            </Typography>
          </Box>
          <Box>
            <Typography variant="subtitle2">
              Автор: {location.author.username}
            </Typography>
          </Box>
        </Box>

        {/* Рейтинг */}
        <Box sx={{ mt: 3, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Рейтинг
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <MuiRating
              value={location.average_rating}
              readOnly
              precision={0.5}
              icon={<SportsTennisIcon fontSize="inherit" color="primary" />}
              emptyIcon={<SportsTennisIcon fontSize="inherit" color="disabled" />}
            />
            <Typography variant="body2" color="text.secondary">
              ({location.ratings_count} оценок)
            </Typography>
          </Box>

          {/* Форма добавления рейтинга */}
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Ваша оценка:
            </Typography>
            <MuiRating
              value={userRating}
              onChange={(_, value) => setUserRating(value)}
              precision={1}
              icon={<SportsTennisIcon fontSize="inherit" color="primary" />}
              emptyIcon={<SportsTennisIcon fontSize="inherit" color="disabled" />}
            />
          </Box>

          {/* Список отзывов */}
          {ratings.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                Отзывы:
              </Typography>
              {ratings.map((rating) => (
                <Box key={rating.id} sx={{ mb: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <MuiRating value={rating.score} readOnly size="small" />
                    <Typography variant="body2" color="text.secondary">
                      {rating.user.username}
                    </Typography>
                  </Box>
                  {rating.comment && (
                    <Typography variant="body2">
                      {rating.comment}
                    </Typography>
                  )}
                </Box>
              ))}
            </Box>
          )}
        </Box>
      </Box>
    </Modal>
  );
} 
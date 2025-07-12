import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Icon } from 'leaflet';
import { useEffect, useState } from 'react';
import axios from 'axios';
import LocationModal from './LocationModal';
import FilterPanel from './FilterPanel';
import { Rating as MuiRating } from '@mui/material';
import AddLocationModal from './AddLocationModal';
import { Map as LeafletMap } from 'leaflet';
import { IconButton, Box } from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';

// Фикс для иконок маркеров
const icon = new Icon({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

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
    url?: string;
  }>;
  average_rating: number;
  ratings_count: number;
}

export default function Map() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [filters, setFilters] = useState({
    hasRoof: false,
    netTypes: [] as string[],
  });
  const [newPoint, setNewPoint] = useState<{ lat: number; lng: number } | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [openFilter, setOpenFilter] = useState(true);

  // Получаем уникальные типы сеток из всех локаций
  const availableNetTypes = Array.from(new Set(locations.map(loc => loc.net_type))).filter(Boolean);
  const hasRoofAvailable = locations.some(loc => loc.has_roof);

  useEffect(() => {
    // Загрузка точек с сервера
    const fetchLocations = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/locations');
        setLocations(response.data);
      } catch (error) {
        console.error('Error fetching locations:', error);
      }
    };

    fetchLocations();
  }, []);

  const handleMarkerClick = async (locationId: number) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/locations/${locationId}`);
      setSelectedLocation(response.data);
      setIsModalOpen(true);
    } catch (error) {
      console.error('Error fetching location details:', error);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedLocation(null);
  };

  const handleFilterChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
  };

  const filteredLocations = locations.filter(location => {
    if (filters.hasRoof && !location.has_roof) return false;
    if (filters.netTypes.length > 0 && !filters.netTypes.includes(location.net_type)) return false;
    return true;
  });

  // Обработчик клика по карте
  const handleMapClick = (e: any) => {
    setNewPoint({ lat: e.latlng.lat, lng: e.latlng.lng });
    setIsAddModalOpen(true);
  };

  // Добавление новой точки после успешной отправки формы
  const handleAddLocation = (newLocation: Location) => {
    // Добавляем url для всех фото, если его нет
    const photosWithUrl = (newLocation.photos || []).map(photo => ({
      ...photo,
      url: photo.url ? photo.url : (photo.file_path ? `/static/photos/${photo.file_path}` : ''),
    }));
    setLocations((prev) => [
      ...prev,
      { ...newLocation, photos: photosWithUrl as { id: number; file_path: string; url: string }[] }
    ]);
    setIsAddModalOpen(false);
    setNewPoint(null);
  };

  return (
    <>
      {/* Кнопка открытия/закрытия фильтра */}
      <Box sx={{ position: 'absolute', top: 20, right: 20, zIndex: 1200 }}>
        <IconButton
          onClick={() => setOpenFilter((prev) => !prev)}
          color={openFilter ? 'primary' : 'default'}
          size="large"
          sx={{ bgcolor: 'background.paper', boxShadow: 2 }}
        >
          <FilterListIcon />
        </IconButton>
      </Box>

      <MapContainer
        center={[55.7558, 37.6173]} // Москва
        zoom={11}
        style={{ height: '100vh', width: '100%' }}
        whenReady={(e: { target: LeafletMap }) => {
          e.target.on('click', handleMapClick);
        }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {filteredLocations.map((location) => (
          <Marker
            key={location.id}
            position={[location.latitude, location.longitude]}
            icon={icon}
            eventHandlers={{
              click: () => handleMarkerClick(location.id),
            }}
          >
            <Popup>
              <div>
                <h3>{location.name}</h3>
                <p>{location.description}</p>
                {location.average_rating > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '8px' }}>
                    <MuiRating
                      value={location.average_rating}
                      readOnly
                      size="small"
                      precision={0.5}
                    />
                    <span style={{ fontSize: '12px', color: '#666' }}>
                      ({location.ratings_count})
                    </span>
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
        {newPoint && (
          <Marker position={[newPoint.lat, newPoint.lng]} icon={icon} />
        )}
      </MapContainer>

      {/* Фильтр показывается только если openFilter */}
      {openFilter && (
        <FilterPanel
          filters={filters}
          onFilterChange={handleFilterChange}
          availableNetTypes={availableNetTypes}
          hasRoofAvailable={hasRoofAvailable}
        />
      )}

      <LocationModal
        location={selectedLocation}
        open={isModalOpen}
        onClose={handleCloseModal}
      />

      <AddLocationModal
        open={isAddModalOpen}
        onClose={() => { setIsAddModalOpen(false); setNewPoint(null); }}
        lat={newPoint?.lat}
        lng={newPoint?.lng}
        onLocationAdded={handleAddLocation}
        netTypes={availableNetTypes}
      />
    </>
  );
} 
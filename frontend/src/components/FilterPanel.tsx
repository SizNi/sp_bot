import { Box, Typography, Checkbox, FormControlLabel, FormGroup } from '@mui/material';

interface FilterPanelProps {
  filters: {
    hasRoof: boolean;
    netTypes: string[];
  };
  onFilterChange: (filters: {
    hasRoof: boolean;
    netTypes: string[];
  }) => void;
  availableNetTypes: string[];
  hasRoofAvailable: boolean;
}

export default function FilterPanel({ 
  filters, 
  onFilterChange, 
  availableNetTypes,
  hasRoofAvailable 
}: FilterPanelProps) {
  const handleRoofChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({
      ...filters,
      hasRoof: event.target.checked,
    });
  };

  const handleNetTypeChange = (netType: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const newNetTypes = event.target.checked
      ? [...filters.netTypes, netType]
      : filters.netTypes.filter(type => type !== netType);
    onFilterChange({
      ...filters,
      netTypes: newNetTypes,
    });
  };

  return (
    <Box
      sx={{
        position: 'absolute',
        top: 20,
        right: 20,
        bgcolor: 'background.paper',
        borderRadius: 1,
        boxShadow: 1,
        p: 1.2,
        zIndex: 1000,
        minWidth: 150,
        maxWidth: 200,
      }}
    >
      <Typography variant="body2" sx={{ mb: 0.5, fontWeight: 500 }}>
        Фильтры
      </Typography>
      <FormGroup sx={{ gap: 0.5 }}>
        {hasRoofAvailable && (
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.hasRoof}
                onChange={handleRoofChange}
                size="small"
              />
            }
            label={<Typography variant="caption">Только с крышей</Typography>}
            sx={{ ml: 0, mr: 0 }}
          />
        )}
        {availableNetTypes.length > 0 && (
          <Box sx={{ mt: 0.5 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 0.2 }}>
              Тип сетки:
            </Typography>
            {availableNetTypes.includes('металлическая') && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={filters.netTypes.includes('металлическая')}
                    onChange={handleNetTypeChange('металлическая')}
                    size="small"
                  />
                }
                label={<Typography variant="caption">Металлическая</Typography>}
                sx={{ ml: 0, mr: 0 }}
              />
            )}
            {availableNetTypes.includes('нормальная') && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={filters.netTypes.includes('нормальная')}
                    onChange={handleNetTypeChange('нормальная')}
                    size="small"
                  />
                }
                label={<Typography variant="caption">Нормальная</Typography>}
                sx={{ ml: 0, mr: 0 }}
              />
            )}
            {availableNetTypes.includes('нет сетки') && (
              <FormControlLabel
                control={
                  <Checkbox
                    checked={filters.netTypes.includes('нет сетки')}
                    onChange={handleNetTypeChange('нет сетки')}
                    size="small"
                  />
                }
                label={<Typography variant="caption">Нет сетки</Typography>}
                sx={{ ml: 0, mr: 0 }}
              />
            )}
          </Box>
        )}
      </FormGroup>
    </Box>
  );
} 
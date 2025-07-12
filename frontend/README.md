# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config({
  extends: [
    // Remove ...tseslint.configs.recommended and replace with this
    ...tseslint.configs.recommendedTypeChecked,
    // Alternatively, use this for stricter rules
    ...tseslint.configs.strictTypeChecked,
    // Optionally, add this for stylistic rules
    ...tseslint.configs.stylisticTypeChecked,
  ],
  languageOptions: {
    // other options...
    parserOptions: {
      project: ['./tsconfig.node.json', './tsconfig.app.json'],
      tsconfigRootDir: import.meta.dirname,
    },
  },
})
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config({
  plugins: {
    // Add the react-x and react-dom plugins
    'react-x': reactX,
    'react-dom': reactDom,
  },
  rules: {
    // other rules...
    // Enable its recommended typescript rules
    ...reactX.configs['recommended-typescript'].rules,
    ...reactDom.configs.recommended.rules,
  },
})
```

# Table Tennis Spots Map

## Запуск проекта (dev)

1. **Бэкенд (FastAPI):**
   - Перейдите в корень проекта (где app/main.py)
   - Активируйте виртуальное окружение
   - Запустите сервер:
     ```bash
     uvicorn app.main:app --reload
     ```
   - Сервер будет доступен по адресу: http://localhost:8000

2. **Фронтенд (React + Vite):**
   - Перейдите в папку frontend
   - Установите зависимости:
     ```bash
     npm install
     ```
   - Запустите dev-сервер:
     ```bash
     npm run dev
     ```
   - Фронтенд будет доступен по адресу: http://localhost:5173

## Особенность отображения фотографий в dev-режиме

- В компоненте LocationModal.tsx для корректного отображения фотографий используется абсолютный путь:
  ```tsx
  src={`http://localhost:8000${photo.url}`}
  ```
- Это связано с тем, что в dev-режиме Vite не проксирует статику на FastAPI, и относительный путь не работает.
- **После деплоя на сервер** (или при правильной настройке прокси в vite.config.ts) можно будет использовать относительный путь (`photo.url`).

---

Если потребуется помощь с деплоем или настройкой прокси — см. документацию Vite и FastAPI или обратитесь к разработчику.

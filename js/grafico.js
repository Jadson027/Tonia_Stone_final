document.querySelectorAll('.item').forEach(item => {
    item.addEventListener('click', () => {
      const colorClass = item.getAttribute('data-color');
      const overlayCircle = document.getElementById('overlay-circle');
  
      // Remove todas as classes de cor do overlay-circle
      overlayCircle.classList.remove('primary', 'secondary', 'accent', 'muted');
  
      // Adiciona a classe correspondente à cor
      overlayCircle.classList.add(colorClass);
    });
  });
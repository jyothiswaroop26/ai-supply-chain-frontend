# UI Styling Guide - AI Supply Chain Dashboard

## Overview

The `app/styles/custom.css` file contains comprehensive styling improvements for the AI Supply Chain Dashboard. This guide explains the color palette, components, and how to extend the styling.

---

## Color Palette

### Primary Colors
- **Primary**: `#1f77e0` - Main brand color for interactive elements
- **Primary Dark**: `#1558a8` - Darker shade for hover/active states
- **Primary Light**: `#4fa3ff` - Lighter shade for backgrounds

### Status Colors
- **Success**: `#2ecc71` - Green for successful operations
- **Warning**: `#f39c12` - Orange for warnings
- **Danger**: `#e74c3c` - Red for errors/critical alerts
- **Info**: `#3498db` - Blue for informational messages

### Neutral Colors
- **Dark BG**: `#0f1419` - Sidebar and dark backgrounds
- **Light BG**: `#ffffff` - Main content background
- **Card BG**: `#f8f9fa` - Secondary background
- **Border**: `#e0e0e0` - Border and divider color
- **Text Primary**: `#1a1a1a` - Main text color
- **Text Secondary**: `#666666` - Secondary/muted text
- **Text Light**: `#999999` - Light/subtle text

---

## CSS Variables

All colors and spacing are defined as CSS variables in the `:root` selector, making them easy to customize:

```css
:root {
  --primary-color: #1f77e0;
  --spacing-md: 16px;
  --radius-lg: 12px;
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12);
  /* ... and more */
}
```

To customize, simply modify these variables at the top of `custom.css`.

---

## Component Styling

### Metric Cards
Enhanced KPI/metric cards with:
- Subtle gradient background
- Hover effects with elevation
- Smooth transitions
- Better visual hierarchy

Example:
```python
st.metric("Total Records", "1,234", "Data points")
```

### Buttons
Styled with:
- Gradient backgrounds
- Hover elevation effect
- Disabled state styling
- Smooth transitions

### Input Fields
- Consistent border styling
- Focus states with colored outline
- Clear visual feedback
- Accessible font sizing

### Data Tables
- Hover row highlighting
- Styled headers with primary color
- Border radius for rounded corners
- Better visual separation

### Sidebar
- Dark theme with gradient
- Primary color accent border
- Better contrast for text
- Improved navigation visibility

### Alerts
Four distinct alert styles:
- **Info**: Light blue background with blue left border
- **Success**: Light green background with green left border
- **Warning**: Light orange background with orange left border
- **Error**: Light red background with red left border

---

## Spacing System

Consistent spacing using a scale:

```css
--spacing-xs: 4px    /* Extra small */
--spacing-sm: 8px    /* Small */
--spacing-md: 16px   /* Medium (default) */
--spacing-lg: 24px   /* Large */
--spacing-xl: 32px   /* Extra large */
```

---

## Border Radius

Four levels of roundness:

```css
--radius-sm: 4px     /* Subtle */
--radius-md: 8px     /* Default */
--radius-lg: 12px    /* Rounded cards */
--radius-xl: 16px    /* Extra rounded */
```

---

## Shadow System

Four levels of shadows for depth:

```css
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.08)       /* Subtle */
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.12)      /* Default */
--shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.16)      /* Pronounced */
--shadow-xl: 0 12px 32px rgba(0, 0, 0, 0.20)     /* Deep */
```

---

## Responsive Design

The CSS includes responsive breakpoints:

- **Tablet**: `768px` - Adjusts font sizes and spacing
- **Mobile**: `480px` - Further optimizations for small screens

Elements automatically adapt for smaller screens without needing media query classes.

---

## Dark Mode Support

The CSS includes automatic dark mode support using:

```css
@media (prefers-color-scheme: dark) {
  /* Dark mode colors */
}
```

Colors automatically adjust based on the user's system preferences or Streamlit's theme settings.

---

## Animations

Three built-in animations:

### Fade In
```css
.fade-in {
  animation: fadeIn var(--transition-normal) ease-in-out;
}
```

### Slide In Left
```css
.slide-in-left {
  animation: slideInLeft var(--transition-normal) ease-in-out;
}
```

### Pulse
```css
.pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

Apply these to elements to add smooth animations:

```html
<div class="fade-in">Fades in smoothly</div>
```

---

## Utility Classes

Quick styling with utility classes:

### Text Utilities
```css
.text-center      /* Center align text */
.text-right       /* Right align text */
.text-bold        /* Bold text (700) */
.text-muted       /* Muted gray text */
.text-success     /* Green text */
.text-warning     /* Orange text */
.text-danger      /* Red text */
.text-info        /* Blue text */
```

### Margin Utilities
```css
.mt-xs .mt-sm .mt-md .mt-lg .mt-xl   /* Margin top */
.mb-xs .mb-sm .mb-md .mb-lg .mb-xl   /* Margin bottom */
```

### Padding Utilities
```css
.p-xs .p-sm .p-md .p-lg .p-xl   /* Padding all sides */
```

### Border Radius Utilities
```css
.rounded-sm .rounded-md .rounded-lg .rounded-xl
```

### Shadow Utilities
```css
.shadow-sm .shadow-md .shadow-lg .shadow-xl
```

---

## Customization Guide

### Changing Colors

1. Open `app/styles/custom.css`
2. Find the `:root` section at the top
3. Modify the color variables:

```css
:root {
  --primary-color: #YOUR_COLOR;
  /* ... other colors */
}
```

### Changing Spacing

Modify spacing variables in `:root`:

```css
--spacing-md: 20px;  /* Increase from 16px */
```

### Adding New Component Styles

Add new CSS rules before the utility classes section:

```css
.my-custom-card {
  background: var(--light-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-md);
}
```

### Using Variables in HTML/Markdown

Custom CSS variables work in inline HTML:

```python
st.markdown("""
  <div style="color: var(--primary-color); font-size: 1.25rem;">
    Custom styled text
  </div>
""", unsafe_allow_html=True)
```

---

## Integration with Streamlit

The CSS is automatically loaded by the `streamlit_app.py` file through the `load_custom_css()` function.

**CSS is injected at page load**, so all components automatically inherit the styling.

---

## File Structure

```
app/
├── styles/
│   └── custom.css          # All styling
├── components/
│   ├── data_upload.py
│   ├── data_view.py
│   ├── forecast_view.py
│   └── kpi.py
├── streamlit_app.py        # Main app (loads CSS)
└── __init__.py

.streamlit/
└── config.toml            # Streamlit config with theme
```

---

## Best Practices

1. **Use CSS Variables**: Always use `var(--color)` instead of hardcoding colors
2. **Maintain Consistency**: Use the spacing and sizing scales
3. **Test Responsive**: Check how changes look on mobile (480px)
4. **Dark Mode**: Ensure components work in both light and dark themes
5. **Accessibility**: Maintain sufficient contrast for text (WCAG AA)

---

## Browser Support

The CSS uses modern features but is compatible with:
- Chrome/Edge 88+
- Firefox 87+
- Safari 14+
- Mobile browsers

---

## Performance Notes

- The CSS file is minified in production builds
- CSS variables have excellent browser support
- No external font imports (uses system fonts for performance)
- Smooth transitions use `will-change` sparingly

---

## Troubleshooting

### Styles not appearing?
1. Clear browser cache (Ctrl+Shift+R)
2. Restart the Streamlit server
3. Check browser console for CSS errors
4. Verify `custom.css` exists in `app/styles/`

### Colors look different?
1. Check system dark mode setting
2. Look for media query rules in CSS
3. Verify theme in `.streamlit/config.toml`

### Hover effects not working?
- Ensure JavaScript is enabled
- Check for CSS specificity conflicts
- Test in different browser

---

## Additional Resources

- [Streamlit Theming](https://docs.streamlit.io/library/get-started/main-concepts#theming)
- [CSS Variables (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [Color Accessibility](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)

---

## Version History

- **v1.0** (2026-05-12) - Initial comprehensive styling system
  - Complete CSS variable system
  - Responsive design
  - Dark mode support
  - Animation library
  - Utility classes
  - Streamlit component overrides

---

## Support

For styling questions or improvements, refer to this guide or check the inline comments in `custom.css`.

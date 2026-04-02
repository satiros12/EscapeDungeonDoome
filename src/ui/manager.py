"""
UI Manager - manages all UI components in the game.

The UIManager coordinates the lifecycle of UI components, handling
registration, activation, updates, and rendering. It provides a
centralized interface for controlling which UI elements are visible
and active at any given time.
"""

from typing import Dict, Optional
import pygame

from .interfaces import IUIComponent, IUIManager


class UIManager(IUIManager):
    """
    Manages UI components in the game.

    The UIManager maintains a registry of UI components and controls
    which components are active at any time. Only the active component
    receives update and render calls, though all components remain
    registered for potential activation.

    Attributes:
        _components: Dictionary mapping component names to component instances.
        _active_name: Name of the currently active component, or None if none active.

    Example:
        >>> manager = UIManager()
        >>> manager.register("menu", main_menu)
        >>> manager.register("hud", hud)
        >>> manager.set_active("menu")
        >>> # Now only menu will update and render
    """

    def __init__(self) -> None:
        """Initialize the UI manager with an empty component registry."""
        self._components: Dict[str, IUIComponent] = {}
        self._active_name: Optional[str] = None

    @property
    def active_component(self) -> Optional[str]:
        """Get the name of the currently active component."""
        return self._active_name

    def register(self, name: str, component: IUIComponent) -> None:
        """
        Register a UI component with the manager.

        If a component with the same name already exists, it will be replaced.

        Args:
            name: Unique identifier for the component.
            component: The UI component to register.
        """
        self._components[name] = component

    def get(self, name: str) -> Optional[IUIComponent]:
        """
        Get a registered component by name.

        Args:
            name: Name of the component to retrieve.

        Returns:
            The component if found, None otherwise.
        """
        return self._components.get(name)

    def set_active(self, name: str) -> None:
        """
        Set the active component by name.

        If the component exists, it will be shown and any previously
        active component will be hidden. If the component doesn't exist,
        the current active component will be hidden and no new component
        will be activated.

        Args:
            name: Name of the component to activate.
        """
        # Hide current active component
        if self._active_name and self._active_name in self._components:
            self._components[self._active_name].hide()

        # Set new active component
        if name and name in self._components:
            self._active_name = name
            self._components[name].show()
        else:
            self._active_name = None

    def update(self, dt: float) -> None:
        """
        Update the active component.

        Only the active component receives update calls.

        Args:
            dt: Delta time in seconds since last update.
        """
        if self._active_name and self._active_name in self._components:
            self._components[self._active_name].update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """
        Render the active component.

        Only the active component is rendered.

        Args:
            surface: Pygame surface to render to.
        """
        if self._active_name and self._active_name in self._components:
            self._components[self._active_name].render(surface)

    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Forward input to the active component.

        Args:
            event: Pygame event to handle.

        Returns:
            True if the event was handled, False otherwise.
        """
        if self._active_name and self._active_name in self._components:
            return self._components[self._active_name].handle_input(event)
        return False

    def show_component(self, name: str) -> None:
        """
        Explicitly show a component without changing active state.

        This is useful for overlay components like HUD that should
        always be visible during gameplay.

        Args:
            name: Name of the component to show.
        """
        if name in self._components:
            self._components[name].show()

    def hide_component(self, name: str) -> None:
        """
        Explicitly hide a component without changing active state.

        Args:
            name: Name of the component to hide.
        """
        if name in self._components:
            self._components[name].hide()

    def clear(self) -> None:
        """Remove all registered components and reset active state."""
        self._components.clear()
        self._active_name = None

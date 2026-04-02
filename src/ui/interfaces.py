"""
UI interfaces for component-based UI architecture.

This module defines the abstract interfaces for UI components and managers,
enabling a clean separation of concerns and modular UI system design.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import pygame


class IUIComponent(ABC):
    """
    Base interface for all UI components.

    All UI components (Menu, HUD, Console) must implement this interface
    to be managed by the UIManager. This ensures consistent behavior
    across all UI elements.

    Attributes:
        active: Whether the component is currently visible and updating.
    """

    @property
    @abstractmethod
    def active(self) -> bool:
        """Check if the component is currently active (visible)."""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the component's internal state.

        Args:
            dt: Delta time in seconds since last update.
        """
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """
        Render the component to the given surface.

        Args:
            surface: Pygame surface to render to.
        """
        pass

    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input events.

        Args:
            event: Pygame event to handle.

        Returns:
            True if the event was handled by this component, False otherwise.
        """
        pass

    @abstractmethod
    def show(self) -> None:
        """Show the component, making it visible and active."""
        pass

    @abstractmethod
    def hide(self) -> None:
        """Hide the component, making it invisible and inactive."""
        pass


class IUIManager(ABC):
    """
    Interface for UI management.

    The UIManager coordinates all UI components, handling registration,
    activation, updates, and rendering. This abstraction allows for
    easy swapping of UI implementations and enables centralized
    UI state management.

    Attributes:
        active_component: Name of the currently active UI component.
    """

    @property
    @abstractmethod
    def active_component(self) -> Optional[str]:
        """Get the name of the currently active component."""
        pass

    @abstractmethod
    def register(self, name: str, component: IUIComponent) -> None:
        """
        Register a UI component with the manager.

        Args:
            name: Unique identifier for the component.
            component: The UI component to register.
        """
        pass

    @abstractmethod
    def get(self, name: str) -> Optional[IUIComponent]:
        """
        Get a registered component by name.

        Args:
            name: Name of the component to retrieve.

        Returns:
            The component if found, None otherwise.
        """
        pass

    @abstractmethod
    def set_active(self, name: str) -> None:
        """
        Set the active component by name.

        Only the active component will receive updates and render calls.
        Other components remain registered but hidden.

        Args:
            name: Name of the component to activate.
        """
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update all active components.

        Args:
            dt: Delta time in seconds since last update.
        """
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """
        Render all active components.

        Components are rendered in the order they were registered.

        Args:
            surface: Pygame surface to render to.
        """
        pass

    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Forward input to the active component.

        Args:
            event: Pygame event to handle.

        Returns:
            True if the event was handled, False otherwise.
        """
        pass

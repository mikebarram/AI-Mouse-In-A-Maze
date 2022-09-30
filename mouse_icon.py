import math

import pygame


class MouseIcon(pygame.sprite.Sprite):
    """Mouse icon"""

    def __init__(self):
        super().__init__()
        # mouse.png 40x65
        # https://flyclipart.com/lab-mouse-template-clip-art-free-mouse-clipart-791054#
        self.image = pygame.image.load("images/mouse.png")
        self.rect = self.image.get_rect()
        self.image_original = self.image
        self.rect_original = self.rect

    def update(self, pos_x, pos_y, angle_radians):
        """update the mouse icon to rotate it"""
        self.image, self.rect = self.rot_center(
            self.image_original, self.rect_original, angle_radians
        )
        self.rect.center = [pos_x, pos_y]

    def rot_center(self, image, rect, angle_radians):
        """rotate an image while keeping its center"""
        rot_image = pygame.transform.rotate(image, 270 - math.degrees(angle_radians))
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image, rot_rect

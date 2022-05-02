from django.db import models
from django.utils.translation import gettext_lazy as _

from account.models import User

# Create your models here.


class Todo(models.Model):
    choice = (
        ('created', 'created'),
        ('doing', 'doing'),
        ('done', 'done'),
    )

    owner = models.ForeignKey(User, verbose_name=_('owner'), on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('Todo title'), max_length=150)
    description = models.TextField(verbose_name=_('Todo description'), blank=True)
    status = models.CharField(verbose_name=_('Status'), default='created', max_length=7)
    updated = models.DateTimeField(_("Date Updated"), auto_now=True)
    created = models.DateTimeField(verbose_name=_('Date created'), auto_now_add=True)

    class Meta:
        verbose_name = _('Todo')
        verbose_name_plural = _('Todos')
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.title

    
        

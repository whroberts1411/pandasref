from django.db import models

#------------------------------------------------------------------------------
class AppliesTo(models.Model):
    """ Lookup table - Series, DataFrame or Both.  """

    appliesto = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.appliesto

#------------------------------------------------------------------------------
class Category(models.Model):
    """ The high-level category that the command is part of; for example
        search, filter, transform, markdown, import, etc.  """

    category = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.category

#------------------------------------------------------------------------------
class PandasRef(models.Model):
    """ Main table of command reference details. """

    command = models.CharField(max_length=100)
    appliesto = models.ForeignKey(AppliesTo, blank=True, null=True, on_delete=models.CASCADE)
    example = models.CharField(max_length=200)
    description = models.TextField(null=True)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    inplace = models.BooleanField(default=False, null=True)
    
#------------------------------------------------------------------------------

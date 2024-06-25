from django.contrib import admin

from .models.sprints import Sprints
from .models.tasks import Tasks
from .models.stories import Stories
from .models.projects import Projects
from .models.products import Products
from .models.updates import Updates
from .models.versions import Versions
from .models.personnes import Personnes
from .models.holidays import Holidays
from .models.projects_customers import ProjectsCustomers
from .models.availability import Availability
from .models.workload import Workload
from .models.epic import Epic
from .models.stories_epic import Stories_epic
from import_export.admin import ImportExportModelAdmin


@admin.register(Tasks)
class TasksAdmin(ImportExportModelAdmin):
    pass


@admin.register(Projects)
class ProjectsAdmin(ImportExportModelAdmin):
    pass


@admin.register(Updates)
class UpdatesAdmin(ImportExportModelAdmin):
    pass


@admin.register(Versions)
class VersionsAdmin(ImportExportModelAdmin):
    pass


@admin.register(Products)
class ProductsAdmin(ImportExportModelAdmin):
    pass


@admin.register(ProjectsCustomers)
class ProjectsAdmin(ImportExportModelAdmin):
    pass


@admin.register(Stories)
class StoriesAdmin(ImportExportModelAdmin):
    pass


@admin.register(Personnes)
class PersonnesAdmin(ImportExportModelAdmin):
    pass


@admin.register(Holidays)
class HolidaysAdmin(ImportExportModelAdmin):
    pass


@admin.register(Availability)
class AvailabilityAdmin(ImportExportModelAdmin):
    pass


@admin.register(Workload)
class WorkloadAdmin(ImportExportModelAdmin):
    pass


@admin.register(Sprints)
class SprintsAdmin(ImportExportModelAdmin):
    pass


@admin.register(Epic)
class EpicAdmin(ImportExportModelAdmin):
    pass


@admin.register(Stories_epic)
class Stories_epicAdminAdmin(ImportExportModelAdmin):
    pass

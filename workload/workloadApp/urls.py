from django.urls import path
from django.views.generic import DetailView

from .models.sprints import Sprints
from .models.tasks import Tasks
from .views import home, personnes, tasks, incoming, sprints, updates, projects_customers, projects, products, versions, \
    dashboard, epic, epic_storie, roadmap
from .views.personnes import PersonneDetailView
from .views.roadmap import roadmap_view
from .views.sprints import SprintDetailView

urlpatterns = [
    path("", home.index, name="home"),

    # Url for person
    path("personnes", personnes.personne_list, name="personnes"),
    path('personnes/<int:pk>/', PersonneDetailView.as_view(), name='detail_personne'),

    # Url for incoming
    path("incoming", incoming.index, name="incoming"),

    # Url for projects_custom
    path("projects_customers", projects_customers.projects_customers_list, name='projects_customers'),

    # Url for products
    path("products", products.products_list, name='products'),

    # Url for projects
    path("projects", projects.projects_list, name='projects'),

    # Url for versions
    path("versions", versions.versions_list, name='versions'),
    path("versions/details/<int:pk>/", versions.version_detail, name='version_detail'),

    # Url for tasks
    path("tasks", tasks.tasks_list, name="tasks"),

    # Url for sprints
    path('sprints/<int:pk>/', sprints.sprint_detail, name='sprint_detail'),
    path("sprints", sprints.sprint_list, name="sprints"),

    # Url for dashboard
    path("dashboard", dashboard.dashboard_view, name='dashboard'),

    path('roadmap', roadmap_view, name='roadmap'),

    # Url for dashboard
    path("epic", epic.epics_list, name="epic"),
    path("epic_storie", epic_storie.epics_list, name="epic_storie"),

    # Url for updates
    path("updates", updates.update_view, name='updates'),
    path("updates/task", updates.import_task_from_jira, name='updates_import_task'),
    path("updates/task/delete", updates.clear_all_task, name='updates_clear_all_task'),
    path("updates/project/<int:pk>/", updates.import_projects_task_from_jira, name='updates_import_project_task'),
    path("updates/project", updates.import_project_from_jira, name='updates_import_project'),
    path("updates/project/all", updates.import_all_projects_task_from_jira, name='import_all_projects_task_from_jira'),
    path("updates/product", updates.import_product_from_jira, name='import_product_from_jira'),
    path("updates/product/<int:pk>/", updates.updates_import_product_stories, name='updates_import_product_stories'),
    path("updates/product/all", updates.import_all_products_stories_from_jira,
         name='import_all_products_stories_from_jira'),
    path("updates/epic", updates.import_all_epic_from_jira, name="import_all_epic_from_jira"),
    path("updates/epic_story", updates.import_all_epic_storie_from_jira, name="import_all_epic_storie_from_jira"),
    path("updates/synchroJira", updates.clear_outdated_data, name='clear_outdated_data'),
    path("updates/projectCustomer", updates.import_all_project_customer_stories_from_jira,
         name='import_project_customer_from_jira'),
    path("updates/projectCustomer/<int:pk>/", updates.updates_import_projects_customers_stories,
         name='updates_import_projects_customers_stories'),
    path("updates/holidays", updates.delete_and_update_holidays, name='delete_and_update_holidays'),
    path("updates/availability", updates.calculate_unavailability_per_person_per_month,
         name='calculate_unavailability_per_person_per_month'),
    path("updates/workload", updates.calculate_workload_per_person_per_month,
         name='calculate_workload_per_person_per_month'),
    path("updates/sysadmin", updates.updates_admin_task, name='updates_admin_task'),
]

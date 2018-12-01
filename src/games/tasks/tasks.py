from celery.utils.log import get_task_logger
from games.celery import app
from games import models
from games.business_logic import db_default_values
from games.models import User

logger = get_task_logger(__name__)


@app.task()
def create_staff():
    user = User.objects.create_user(username='staff', password='staff')
    user.is_staff = True
    user.save()
    logger.info('Staff added')


@app.task(retry_backoff=True)
def set_default_values():
    logger.info('Start task for setting default values')

    # TRUNCATE TABLES
    models.DefinitionQuestion.objects.all().delete()
    models.CompoundQuestion.objects.all().delete()
    models.FunctionalQuestion.objects.all().delete()
    models.Color.objects.all().delete()
    models.Category.objects.all().delete()
    models.Form.objects.all().delete()
    models.Material.objects.all().delete()
    models.SubCategory.objects.all().delete()
    models.Quantity.objects.all().delete()

    # POPULATE
    models.DefinitionQuestion.populate(db_default_values.DEFINITION_QUESTION)
    models.CompoundQuestion.populate(db_default_values.COMPOUND_QUESTIONS)
    models.FunctionalQuestion.populate(db_default_values.FUNCTIONAL_QUESTIONS)
    models.Color.populate(db_default_values.COLOR)
    models.Category.populate(db_default_values.CATEGORIES)
    models.Form.populate(db_default_values.FORM)
    models.Material.populate(db_default_values.MATERIAL)
    models.Quantity.populate(db_default_values.QUANTITY)

    models.SubCategory.populate(db_default_values.TRANSPORT)
    models.SubCategory.populate(db_default_values.EQUIPMENT)
    models.SubCategory.populate(db_default_values.TOYS)
    models.SubCategory.populate(db_default_values.FURNITURE)
    models.SubCategory.populate(db_default_values.THINGS)
    models.SubCategory.populate(db_default_values.PLANTS)
    models.SubCategory.populate(db_default_values.BATH_ACCESSORIES)
    models.SubCategory.populate(db_default_values.STATIONERY)
    models.SubCategory.populate(db_default_values.INSTRUMENTS)
    models.SubCategory.populate(db_default_values.FOOD)
    models.SubCategory.populate(db_default_values.SPORTS_EQUIPMENT)
    models.SubCategory.populate(db_default_values.FOOTWEAR)
    models.SubCategory.populate(db_default_values.CLOTHES)
    models.SubCategory.populate(db_default_values.BIRDS)
    models.SubCategory.populate(db_default_values.WILDS)
    models.SubCategory.populate(db_default_values.PETS)
    models.SubCategory.populate(db_default_values.DISHES)
    models.SubCategory.populate(db_default_values.MUSICAL_INSTRUMENTS)
    models.SubCategory.populate(db_default_values.VEGETABLES)
    models.SubCategory.populate(db_default_values.FRUITS)

    logger.info('Backup was completed')

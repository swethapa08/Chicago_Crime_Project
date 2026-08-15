from . import db


class ChicagoCrime(db.Model):

    __tablename__ = "crimes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    case_number = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    date = db.Column(
        db.DateTime
    )

    block = db.Column(
        db.String(150)
    )

    iucr_code = db.Column(
        db.String(20)
    )

    primary_type = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.String(200)
    )

    location_desc = db.Column(
        db.String(150)
    )

    arrest = db.Column(
        db.Integer
    )

    domestic = db.Column(
        db.Integer
    )

    beat_num = db.Column(
        db.Integer
    )

    district_code = db.Column(
        db.String(20)
    )

    ward_no = db.Column(
        db.Float
    )

    community_code = db.Column(
        db.String(20)
    )

    fbi_code = db.Column(
        db.String(50)
    )

    x_coordinate = db.Column(
        db.Float
    )

    y_coordinate = db.Column(
        db.Float
    )

    date_of_update = db.Column(
        db.String(50)
    )

    latitude = db.Column(
        db.Float
    )

    longitude = db.Column(
        db.Float
    )

    location = db.Column(
        db.String(150)
    )

    Year = db.Column(
        db.Integer
    )

    DayOfWeek = db.Column(
        db.String(20)
    )

    Month = db.Column(
        db.Integer
    )


class IUCRCode(db.Model):

    __tablename__ = "iucr_codes"

    iucr_code = db.Column(
        db.String(20),
        primary_key=True
    )

    primary_type = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.String(200)
    )

    index_code = db.Column(
        db.String(20)
    )


class PoliceBeat(db.Model):

    __tablename__ = "police_beats"

    beat_num = db.Column(
        db.Integer,
        primary_key=True
    )

    district = db.Column(
        db.Integer
    )

    sector = db.Column(
        db.Integer
    )

    beat = db.Column(
        db.Integer
    )


class DistrictPS(db.Model):

    __tablename__ = "district_ps_info"

    district_code = db.Column(
        db.Integer,
        primary_key=True
    )

    district_name = db.Column(
        db.String(100)
    )

    address = db.Column(
        db.String(200)
    )

    city = db.Column(
        db.String(50)
    )

    state = db.Column(
        db.String(20)
    )

    zip = db.Column(
        db.String(20)
    )

    website = db.Column(
        db.String(300)
    )

    phone = db.Column(
        db.String(50)
    )

    fax = db.Column(
        db.String(50)
    )

    tty = db.Column(
        db.String(50)
    )

    x_coordinate = db.Column(
        db.Float
    )

    y_coordinate = db.Column(
        db.Float
    )

    latitude = db.Column(
        db.Float
    )

    longitude = db.Column(
        db.Float
    )

    location = db.Column(
        db.String(200)
    )


class WardOffice(db.Model):

    __tablename__ = "ward_office"

    ward_no = db.Column(
        db.Integer,
        primary_key=True
    )

    alderman = db.Column(
        db.String(150)
    )

    address = db.Column(
        db.String(200)
    )

    city = db.Column(
        db.String(50)
    )

    state = db.Column(
        db.String(20)
    )

    zipcode = db.Column(
        db.String(20)
    )

    ward_phone = db.Column(
        db.String(50)
    )

    ward_fax = db.Column(
        db.String(50)
    )

    email = db.Column(
        db.String(150)
    )

    website = db.Column(
        db.String(300)
    )

    location = db.Column(
        db.String(200)
    )

    city_hall_address = db.Column(
        db.String(200)
    )

    city_hall_city = db.Column(
        db.String(50)
    )

    city_hall_state = db.Column(
        db.String(20)
    )

    city_hall_zipcode = db.Column(
        db.String(20)
    )

    city_hall_phone = db.Column(
        db.String(50)
    )


class CityCommunity(db.Model):

    __tablename__ = "city_community"

    community_code = db.Column(
        db.String(20),
        primary_key=True
    )

    community_name = db.Column(
        db.String(100)
    )

    population = db.Column(
        db.Integer
    )

    area_sqmile = db.Column(
        db.Float
    )

    area_sqkm = db.Column(
        db.Float
    )

    density_per_sqmi = db.Column(
        db.Float
    )

    density_per_sqkm = db.Column(
        db.Float
    )



CREATE DATABASE clinical_study_db;


CREATE TABLE IF NOT EXISTS subjects (
  subject_id INT NOT NULL,           -- Unique identifier for each subject
  site_id VARCHAR(10) NULL,          -- Clinical site identifier
  arm VARCHAR(45) NULL,              -- Treatment arm (e.g., 'Drug X', 'Standard of Care')
  dob DATE NULL,                     -- Date of birth
  gender CHAR(1) NULL,               -- Gender ('F', 'M')
  enroll_date DATE NULL,             -- Study enrollment date
  PRIMARY KEY (subject_id)
);

-- Table: aes
-- Stores Adverse Event information for subjects
-- Relationship: Many adverse events can belong to one subject (Many-to-One)
CREATE TABLE IF NOT EXISTS aes (
  ae_id SERIAL NOT NULL,             -- Unique identifier for each adverse event
  subject_id INT NOT NULL,           -- Foreign key to subjects.subject_id
  ae_term VARCHAR(255) NULL,         -- Description of the adverse event
  severity VARCHAR(45) NULL,         -- Severity ('Mild', 'Moderate', 'Severe', 'Life-threatening')
  start_date DATE NULL,              -- Date when adverse event started
  end_date DATE NULL,                -- Date when adverse event ended (NULL if ongoing)
  related BOOLEAN NULL,              -- Whether related to treatment (TRUE/FALSE)
  PRIMARY KEY (ae_id),
  CONSTRAINT fk_aes_subjects
    FOREIGN KEY (subject_id)
    REFERENCES subjects (subject_id)
);

CREATE INDEX fk_aes_subjects_idx ON aes (subject_id);

-- Table: labs
-- Stores laboratory test results for subjects
-- Relationship: Many lab results can belong to one subject (Many-to-One)
CREATE TABLE IF NOT EXISTS labs (
  lab_id SERIAL NOT NULL,            -- Unique identifier for each lab result
  subject_id INT NOT NULL,           -- Foreign key to subjects.subject_id
  visit VARCHAR(45) NULL,            -- Visit identifier (e.g., 'Baseline', 'Week 1')
  lab_test VARCHAR(45) NULL,         -- Type of lab test (e.g., 'Hemoglobin', 'WBC', 'ALT')
  value FLOAT NULL,                  -- Measured value
  units VARCHAR(45) NULL,            -- Units of measurement (e.g., 'g/dL', 'U/L')
  normal_range VARCHAR(45) NULL,     -- Reference range (e.g., '12-16', '0-40')
  PRIMARY KEY (lab_id),
  CONSTRAINT fk_labs_subjects
    FOREIGN KEY (subject_id)
    REFERENCES subjects (subject_id)
);

CREATE INDEX fk_labs_subjects_idx ON labs (subject_id);

-- Table: tumor_response
-- Stores tumor response assessments (RECIST) for subjects
-- Relationship: Many tumor responses can belong to one subject (Many-to-One)
CREATE TABLE IF NOT EXISTS tumor_response (
  response_id SERIAL NOT NULL,       -- Unique identifier for each response assessment
  subject_id INT NOT NULL,           -- Foreign key to subjects.subject_id
  visit VARCHAR(45) NULL,            -- Visit identifier (e.g., 'Week 8', 'Week 16')
  response VARCHAR(10) NULL,         -- RECIST response ('CR', 'PR', 'SD', 'PD', 'NE')
                                     -- CR=Complete Response, PR=Partial Response
                                     -- SD=Stable Disease, PD=Progressive Disease, NE=Not Evaluable
  assessed_by VARCHAR(45) NULL,      -- Who assessed ('Investigator', 'Independent')
  PRIMARY KEY (response_id),
  CONSTRAINT fk_tumor_response_subjects
    FOREIGN KEY (subject_id)
    REFERENCES subjects (subject_id)
);

CREATE INDEX fk_tumor_response_subjects_idx ON tumor_response (subject_id);





COPY subjects(subject_id, site_id, arm, dob, gender, enroll_date)
FROM 'E:/Dizzaroo Project/Analytic_Project/foramted_data/Subjects.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');




-- Import data into aes table (adverse events)
COPY aes(subject_id, ae_term, severity, start_date, end_date, related)
FROM 'E:/Dizzaroo Project/Analytic_Project/foramted_data/AEs.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Import data into labs table
COPY labs(subject_id, visit, lab_test, value, units, normal_range)
FROM 'E:/Dizzaroo Project/Analytic_Project/foramted_data/Labs.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Import data into tumor_response table
COPY tumor_response(subject_id, visit, response, assessed_by)
FROM 'E:\Dizzaroo Project\Analytic_Project\foramted_data\tumer_response.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');

import 'cypress-file-upload';

describe('Upload Python Code Page (E2E)', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/upload-python');
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  it('should upload a valid Python file and show its name', () => {
    const filePath = 'model_training_and_evaluation/model.py'; 
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "/model.py",
        mimeType: 'text/x-python',
      });
    });
    cy.get('#file-name').should('contain', 'model.py');  
  });

  it('should toggle between analysis modes (AI-Based and Static Tool)', () => {
    cy.contains('AI-Based').click();
    cy.contains('AI-Based').should('have.class', 'bg-red-500');  
    cy.contains('Static Tool').click();
    cy.contains('Static Tool').should('have.class', 'bg-blue-500'); 
  });

  /*it('should upload a file and analyze it in AI-Based mode', () => {
    const filePath = 'sample_files/sample.py';
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "sample.py",
        mimeType: 'text/x-python',
      });
    });
    
    cy.contains('AI-Based').click(); 
    cy.get('button').contains('Upload Code (AI Mode)').click();  

    cy.get('[data-testid="progress"]').should('exist'); 
    cy.wait(5000);  

    cy.contains('Smell #1').should('be.visible');  
    cy.contains('Long function').should('be.visible');
    cy.contains('Line: 12').should('be.visible');
  });*/

  it('should display progress and results in Static Tool mode', () => {
    const filePath = 'model_training_and_evaluation/dataset_preparation.py';
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "dataset_preparation.py",
        mimeType: 'text/x-python',
      });
    });

    cy.contains('Static Tool').click();  
    cy.get('button').contains('Upload Code (Static Mode)').click(); 

    cy.get('[data-testid="progress"]').should('exist');    

    cy.contains('Smell #1').should('be.visible');  
    cy.contains('Smell #2').should('be.visible');
  });

  it('should display no smells message for clean code', () => {
    cy.contains('Static Tool').click();
    const filePath = 'model_training_and_evaluation/pipeline.py';
    cy.fixture(filePath, 'utf8').then((fileContent) => {
      cy.get('[role="file-uploader"]').attachFile({
        fileContent,
        fileName: "pipeline.py",
        mimeType: 'text/x-python',
      });
    });
    cy.contains('Upload Code').click();
    cy.get("#progress").should('contain','Code uploaded and analyzed successfully!')
    cy.contains('No code smells detected! Your code is clean!').should('be.visible');
  });
});

Cypress.config('defaultCommandTimeout', 10000);

describe('UploadPythonPage Integration Tests', () => {

  beforeEach(() => {
    cy.visit('http://localhost:3000/upload-python'); 
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  it('should display the page and file upload section', () => {
    cy.get('header').should('exist'); 
    cy.get('footer').should('exist'); 
    cy.contains('Upload and Analyze Python Code').should('exist'); 
    cy.get('[role="file-uploader"]').should('exist'); 
  });


});

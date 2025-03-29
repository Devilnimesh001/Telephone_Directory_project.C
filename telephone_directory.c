#include <stdio.h>
#include <string.h>

#define FILENAME_SIZE 1024
#define MAX_LINE 2048
int num = 0;

struct telephone
{
    char name[20];
    char number[11];
};

// Function to insert spaces in the file
void space(int len, FILE *file)
{
    char c = ' ';
    
    for (int i = 0; i < len; i++)
    {
        fprintf(file, "%c", c);
    }
}

// Function to write a telephone entry to the file
void write(struct telephone* input, FILE *file)
{
    int len = strlen(input->name);
    int sp_len = 20 - len;
    
    fprintf(file, "%s", input->name);
    space(sp_len, file);
    fprintf(file, "%s\n", input->number);
}

// Function to insert a new entry in the telephone directory
void insertEntry(FILE *file)
{
    static int number = 1;
    printf("Entry number %d: \n",number);
    
    fseek(file, 0, SEEK_END);
    struct telephone newentry;
    
    printf("Enter the Name: ");
    scanf(" %[^\n]s", newentry.name);
    
    printf("Enter the phoneNumber: ");
    scanf(" %[^\n]s", newentry.number);
    
    write(&newentry, file);
    printf("Entry inserted...\n");
    number+=1;
}

// Function to update an existing entry in the telephone directory
void updateEntry(FILE *file)
{
    if (num > 0)
    {
        printf("Give the entry number n-%d...\n",num - 1);
    }
    
    int entrynumber;
    printf("Enter the entry number to update: ");
    scanf("%d", &entrynumber);
    entrynumber += 1;
    fflush(stdin);
    
    fseek(file, (entrynumber - 1) * sizeof(struct telephone), SEEK_SET);
    
    struct telephone existingEntry;
    fread(&existingEntry, sizeof(struct telephone), 1, file);
    
    printf("Enter Updated name: ");
    scanf(" %[^\n]s", existingEntry.name);

    printf("Enter updated phoneNumber: ");
    scanf(" %[^\n]s", existingEntry.number);
    
    fseek(file, (entrynumber - 1) * sizeof(struct telephone), SEEK_SET);
    
    write(&existingEntry, file);
    printf("Updated successfully...\n");
}

// Function to remove a specific line from the file
void RemoveLineFromFile(FILE *file, int line_number)
{
    FILE *temp_file = fopen("temp.txt", "w");
    if (temp_file == NULL)
    {
        printf("Unable to open the temporary file.");
        return;
    }
    
    char buffer[MAX_LINE];
    int current_line = 1;
    
    while (fgets(buffer, MAX_LINE, file) != NULL)
    {
        if (current_line != line_number)
        {
            fputs(buffer, temp_file);
        }
        
        current_line++;
    }
    
    fclose(file);
    fclose(temp_file);
    
    remove("telephone_directory.txt");
    rename("temp.txt", "telephone_directory.txt");
    
    printf("Entry deleted successfully.\n");
}

// Function to delete an entry from the telephone directory
void deleteEntry()
{
    int entrynumber;
    
    if (num > 0)
    {
        printf("Give the entry number n-%d...\n",num);
    }
    
    printf("Enter entry number to delete: ");
    scanf("%d", &entrynumber);
    entrynumber += 1;
    fflush(stdin);
    
    FILE *file = fopen("telephone_directory.txt", "r");
    if (file == NULL)
    {
        printf("Unable to open the file.");
        return;
    }
    
    RemoveLineFromFile(file, entrynumber);
    
    num++;
}

int main()
{
    FILE *file = fopen("telephone_directory.txt", "wb+");
    
    if (file == NULL)
    {
        printf("Unable to create the file.");
        return 1;
    }
    
    fprintf(file, "NAME                    NUMBER\n");
    
    int choice;
    
    while (1)
    {
        printf("Telephone Directory Menu:\n");
        printf("1. Insert an entry\n");
        printf("2. Update an entry\n");
        printf("3. Delete an entry\n");
        printf("4. Exit\n");
        printf("Enter your choice: ");
        scanf("%d", &choice);
        
        switch (choice)
        {
            case 1:
                insertEntry(file);
                break;
            case 2:
                updateEntry(file);
                break;
            case 3:
                fclose(file);
                deleteEntry();
                file = fopen("telephone_directory.txt","r+");
                break;
            case 4:
                fclose(file);
                printf("Exiting...\n");
                return 0;
            default:
                printf("Invalid operation.\n");
        }
        
        printf("\n");
    }
}

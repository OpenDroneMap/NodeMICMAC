/* block.h */
/* Copyright Vladimir Kolmogorov vnk@ist.ac.at */
/* Last modified May 2013 */
/*
	Template classes Block and DBlock
	Implement adding and deleting items of the same type in blocks.

	If there there are many items then using Block or DBlock
	is more efficient than using 'new' and 'delete' both in terms
	of memory and time since
	(1) On some systems there is some minimum amount of memory
	    that 'new' can allocate (e.g., 64), so if items are
	    small that a lot of memory is wasted.
	(2) 'new' and 'delete' are designed for items of varying size.
	    If all items has the same size, then an algorithm for
	    adding and deleting can be made more efficient.
	(3) All Block and DBlock functions are inline, so there are
	    no extra function calls.

	Differences between Block and DBlock:
	(1) DBlock allows both adding and deleting items,
	    whereas Block allows only adding items.
	(2) Block has an additional operation of scanning
	    items added so far (in the order in which they were added).
	(3) Block allows to allocate several consecutive
	    items at a time, whereas DBlock can add only a single item.

	Note that no constructors or destructors are called for items.

	Example usage for items of type 'MyType':

	///////////////////////////////////////////////////
	#include "block.h"
	#define BLOCK_SIZE 1024
	typedef struct { int a, b; } MyType;
	MyType *ptr, *array[10000];

	...

	Block<MyType> *block = new Block<MyType>(BLOCK_SIZE);

	// adding items
	for (int i=0; i<sizeof(array); i++)
	{
		ptr = block -> New();
		ptr -> a = ptr -> b = rand();
	}

	// reading items
	for (ptr=block->ScanFirst(); ptr; ptr=block->ScanNext())
	{
		printf("%d %d\n", ptr->a, ptr->b);
	}

	delete block;

	...

	DBlock<MyType> *dblock = new DBlock<MyType>(BLOCK_SIZE);

	// adding items
	for (int i=0; i<sizeof(array); i++)
	{
		array[i] = dblock -> New();
	}

	// deleting items
	for (int i=0; i<sizeof(array); i+=2)
	{
		dblock -> Delete(array[i]);
	}

	// adding items
	for (int i=0; i<sizeof(array); i++)
	{
		array[i] = dblock -> New();
	}

	delete dblock;

	///////////////////////////////////////////////////

	Note that DBlock deletes items by marking them as
	empty (i.e., by adding them to the list of free items),
	so that this memory could be used for subsequently
	added items. Thus, at each moment the memory allocated
	is determined by the maximum number of items allocated
	simultaneously at earlier moments. All memory is
	deallocated only when the destructor is called.
*/

#ifndef __BLOCK_H__
#define __BLOCK_H__

#include <stdlib.h>

/***********************************************************************/
/***********************************************************************/
/***********************************************************************/

template <class Type> class Block
{
public:
	/* Constructor. Arguments are the block size and
	   (optionally) the pointer to the function which
	   will be called if allocation failed; the message
	   passed to this function is "Not enough memory!" */
	Block(int size, void (*err_function)(const char *) = NULL) { first = last = NULL; block_size = size; error_function = err_function; }

	/* Destructor. Deallocates all items added so far */
	~Block() { while (first) { block *next = first -> next; delete[] ((char*)first); first = next; } }

	/* Allocates 'num' consecutive items; returns pointer
	   to the first item. 'num' cannot be greater than the
	   block size since items must fit in one block */
	Type *New(int num = 1)
	{
		Type *t;

		if (!last || last->current + num > last->last)
		{
			if (last && last->next) last = last -> next;
			else
			{
				block *next = (block *) new char [sizeof(block) + (block_size-1)*sizeof(Type)];
				if (!next) { if (error_function) (*error_function)("Not enough memory!"); exit(1); }
				if (last) last -> next = next;
				else first = next;
				last = next;
				last -> current = & ( last -> data[0] );
				last -> last = last -> current + block_size;
				last -> next = NULL;
			}
		}

		t = last -> current;
		last -> current += num;
		return t;
	}

	/* Returns the first item (or NULL, if no items were added) */
	Type *ScanFirst()
	{
		for (scan_current_block=first; scan_current_block; scan_current_block = scan_current_block->next)
		{
			scan_current_data = & ( scan_current_block -> data[0] );
			if (scan_current_data < scan_current_block -> current) return scan_current_data ++;
		}
		return NULL;
	}

	/* Returns the next item (or NULL, if all items have been read)
	   Can be called only if previous ScanFirst() or ScanNext()
	   call returned not NULL. */
	Type *ScanNext()
	{
		while (scan_current_data >= scan_current_block -> current)
		{
			scan_current_block = scan_current_block -> next;
			if (!scan_current_block) return NULL;
			scan_current_data = & ( scan_current_block -> data[0] );
		}
		return scan_current_data ++;
	}

	struct iterator; // for overlapping scans
	Type *ScanFirst(iterator& i)
	{
		for (i.scan_current_block=first; i.scan_current_block; i.scan_current_block = i.scan_current_block->next)
		{
			i.scan_current_data = & ( i.scan_current_block -> data[0] );
			if (i.scan_current_data < i.scan_current_block -> current) return i.scan_current_data ++;
		}
		return NULL;
	}
	Type *ScanNext(iterator& i)
	{
		while (i.scan_current_data >= i.scan_current_block -> current)
		{
			i.scan_current_block = i.scan_current_block -> next;
			if (!i.scan_current_block) return NULL;
			i.scan_current_data = & ( i.scan_current_block -> data[0] );
		}
		return i.scan_current_data ++;
	}

	/* Marks all elements as empty */
	void Reset()
	{
		block *b;
		if (!first) return;
		for (b=first; ; b=b->next)
		{
			b -> current = & ( b -> data[0] );
			if (b == last) break;
		}
		last = first;
	}

/***********************************************************************/

private:

	typedef struct block_st
	{
		Type					*current, *last;
		struct block_st			*next;
		Type					data[1];
	} block;

	int		block_size;
	block	*first;
	block	*last;
public:
	struct iterator
	{
		block	*scan_current_block;
		Type	*scan_current_data;
	};
private:
	block	*scan_current_block;
	Type	*scan_current_data;

	void	(*error_function)(const char *);
};

/***********************************************************************/
/***********************************************************************/
/***********************************************************************/

template <class Type> class DBlock
{
public:
	/* Constructor. Arguments are the block size and
	   (optionally) the pointer to the function which
	   will be called if allocation failed; the message
	   passed to this function is "Not enough memory!" */
	DBlock(int size, void (*err_function)(const char *) = NULL) { first = NULL; first_free = NULL; block_size = size; error_function = err_function; }

	/* Destructor. Deallocates all items added so far */
	~DBlock() { while (first) { block *next = first -> next; delete[] ((char*)first); first = next; } }

	/* Allocates one item */
	Type *New()
	{
		block_item *item;

		if (!first_free)
		{
			block *next = first;
			first = (block *) new char [sizeof(block) + (block_size-1)*sizeof(block_item)];
			if (!first) { if (error_function) (*error_function)("Not enough memory!"); exit(1); }
			first_free = & (first -> data[0] );
			for (item=first_free; item<first_free+block_size-1; item++)
				item -> next_free = item + 1;
			item -> next_free = NULL;
			first -> next = next;
		}

		item = first_free;
		first_free = item -> next_free;
		return (Type *) item;
	}

	/* Deletes an item allocated previously */
	void Delete(Type *t)
	{
		((block_item *) t) -> next_free = first_free;
		first_free = (block_item *) t;
	}

/***********************************************************************/

private:

	typedef union block_item_st
	{
		Type			t;
		block_item_st	*next_free;
	} block_item;

	typedef struct block_st
	{
		struct block_st			*next;
		block_item				data[1];
	} block;

	int			block_size;
	block		*first;
	block_item	*first_free;

	void	(*error_function)(const char *);
};


/***********************************************************************/
/***********************************************************************/
/***********************************************************************/

// there is no Free() function, just Alloc() that could return the same pointer.
// The allocated space grows as needed.
class ReusableBuffer
{
public:
	/* Constructor. */
	ReusableBuffer(void (*err_function)(const char *) = NULL) : buf(NULL), size_max(0), error_function(err_function) {}
	~ReusableBuffer() { if (buf) free(buf); }

	void* Alloc(int size)
	{
		if (size <= size_max) return buf;
		size_max = (int)(1.2*size_max) + size;
		if (buf) free(buf);
		buf = (char*)malloc(size_max);
		if (!buf) { if (error_function) (*error_function)("Not enough memory!"); exit(1); }
		return buf;
	}
	void* Realloc(int size)
	{
		if (size <= size_max) return buf;
		size_max = (int)(1.2*size_max) + size;
		if (buf) buf = (char*)realloc(buf, size_max);
		else     buf = (char*)malloc(size_max);
		if (!buf) { if (error_function) (*error_function)("Not enough memory!"); exit(1); }
		return buf;
	}

private:
	char* buf;
	int size_max;

	void	(*error_function)(const char *);
};


/***********************************************************************/
/***********************************************************************/
/***********************************************************************/

// Again, no Free() function but different calls to Alloc() return pointers
// to disjoint chunks of memory (unlike ReusableBuffer). Convenient to avoid
// explicit garbage collection.
class Buffer
{
public:
	Buffer(int _default_size, void (*err_function)(const char *) = NULL)
		: default_size(_default_size), buf_first(NULL), error_function(err_function) {}
	~Buffer()
	{
		while (buf_first)
		{
			char* b = (char*) buf_first;
			buf_first = buf_first->next;
			delete [] b;
		}
	}

	void* Alloc(int size)
	{
		if (!buf_first || buf_first->size+size>buf_first->size_max)
		{
			int size_max = 2*size + default_size;
			Buf* b = (Buf*)(new char[sizeof(Buf)+size_max]);
			if (!b) { if (error_function) (*error_function)("Not enough memory!"); exit(1); }
			b->next = buf_first;
			buf_first = b;
			b->size = 0;
			b->size_max = size_max;
			b->arr = (char*)(b+1);
		}
		char* ptr = &buf_first->arr[buf_first->size];
		buf_first->size += size;
		return ptr;
	}
private:
	struct Buf
	{
		int size, size_max;
		char* arr;
		Buf* next;
	};
	int default_size;
	Buf* buf_first;

	void	(*error_function)(const char *);
};

#endif

